from __future__ import annotations

# — Standard library —
import asyncio
import json
import logging
import os
import queue
import time
from threading import Thread
from typing import Dict, List, Tuple

# — Third-party —
import cv2
from openai import OpenAI

# — Application —
from app import get_server_links, game_state, run as run_flask, socketio, state_ready
from audio.GPTTTS import GPTTTS
from audio.audio_stream import AudioStream
from audio.google_transcriber import GoogleStreamingTranscriber
from config.apikeys import OPENAI_API_KEY
from prompt.prompt_builder_emotions import _CLUE_LOOKUP, create_system_prompt

from participant_manager import ParticipantDataManager
from video.camera_stream import CameraStream
from video.emotion_detector import EmotionDetector


# ── parameters ────────────────────────────────────────────────────────────────
IDLE_TIMEOUT  = 20          # seconds with no speech
STT_POLL_SECS = 0.5         # Google queue poll interval
FPS_ANALYSE   = 24         # emotion FPS
USE_ROBOT     = False       # whether to use robot TTS interface


# ──────────────────────────────────────────────────────────────────────────────
def _drain_transcription_queue(q: queue.Queue):
    while not q.empty():
        try:
            q.get_nowait()
        except queue.Empty:
            break 

def _format_emotion_summary(spans: List[Tuple[str, float]]) -> str:
    return " ".join(f"{emo}:{dur:.2f}" for emo, dur in spans)

def _predominant_emotion(spans: List[Tuple[str, float]]) -> str:
    totals: Dict[str, float] = {}
    for emo, dur in spans:
        totals[emo] = totals.get(emo, 0.0) + float(dur)
    return max(totals, key=totals.get) if totals else "neutral" 

def _compute_recently_completed(
    crossword_state: dict,
    completed_set: set[Tuple[str, int]],
) -> List[Tuple[str, int]]:
    recently_completed: List[Tuple[str, int]] = []

    for direction in ("across", "down"):
        for num_str, pattern in crossword_state.get(direction, {}).items():
            if num_str == "undefined" or not pattern or "0" in pattern:
                continue

            num = int(num_str)
            dir_letter = direction[0].upper()
            answer = _CLUE_LOOKUP.get((dir_letter, num), {}).get("answer")

            if answer and pattern == answer and (dir_letter, num) not in completed_set:
                completed_set.add((dir_letter, num))
                recently_completed.append((dir_letter, num))

    return recently_completed


# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # ── Noise suppression ─────────────────────────────────────────────────────
    os.environ["GRPC_VERBOSITY"] = "ERROR"
    logging.getLogger("werkzeug").setLevel(logging.ERROR)
    logging.getLogger("rmn").setLevel(logging.WARNING)

    # ── 1) Start the Flask-SocketIO server (web UI) ───────────────────────────
    Thread(target=run_flask, daemon=True).start() 
    print("[MAIN] Flask-SocketIO server started …") 
    for link in get_server_links():               
        print(f"[SETUP] Open the crossword at: {link}")

    # ── 2) Video / emotion helpers ────────────────────────────────────────────
    cam_stream = CameraStream(camera_index=0, buffer_size=30)  
    emotion_detector = EmotionDetector(cam_stream, fps=FPS_ANALYSE)  
    emotion_detector.start()


    # ── 3) Audio / STT ────────────────────────────────────────────────────────
    audio_stream = AudioStream(
        samplerate=16000,
        channels=1,
        dtype="int16",
        buffer_duration=10.0,
    )
    transcriber = GoogleStreamingTranscriber(audio_stream, "en-US")
    transcriber.start()

    # ── 4) TTS / robot ────────────────────────────────────────────────────────
    tts_manager = GPTTTS(
        api_key=OPENAI_API_KEY,
        use_robot=USE_ROBOT,
        robot_serial_suffix="00233",
        transcriber=transcriber,
    )

    # Event loop for async TTS operations
    _loop = asyncio.new_event_loop()
    asyncio.set_event_loop(_loop)

    # Pause STT while we connect TTS/robot
    transcriber.pause_listening()
    _loop.run_until_complete(tts_manager.connect_robot())

    # Show connection links
    print(f"[SETUP] Connect your browser at: {get_server_links()}")

    # ── 5) Participant / data manager ─────────────────────────────────────────
    participant_id = input("\nParticipant number (anon. ID) ➜ ").strip()
    pdata = ParticipantDataManager(participant_id)
    print(f"[MAIN] created data folder: {pdata.part_dir}")

    # ── 6) Quick countdown before starting ────────────────────────────────────
    print("\n[SETUP] You have 5 s to get ready…")
    for i in range(5, 0, -1):
        print(f"   starting in {i:2d} s ⏳", end="\r", flush=True)
        time.sleep(1)
    print("\n[SETUP] Time’s up – experiment begins!\n")

    # ── 7) Resume STT and prime state ─────────────────────────────────────────
    transcriber.resume_listening()
    _drain_transcription_queue(transcriber.transcription_queue)
    transcriber.last_activity = time.time()

    # ── 8) Conversation state variables ───────────────────────────────────────
    history: List[Dict[str, str]] = []
    prev_idle_log: int = -1
    turn_idx: int = 0
    in_speech: bool = False
    speaking_turn: int | None = None

    # ── 9) Intro utterance ────────────────────────────────────────────────────
    intro_text = (
        "Hey there! I’m ClueBot—your friendly crossword side-kick. "
        "I can see which clue you’re working on and I’ll jump in with hints, "
        "fun facts, or just a bit of banter whenever you like. "
        "If my mouth lamp is glowing green, I’m listening! "
        "Ready when you are—good luck, and let’s crack this puzzle together!"
    )

    pdata.append_timeline("Robot starts speaking (intro)")
    _loop.run_until_complete(tts_manager.speak_text(intro_text)) 

    spans_intro = emotion_detector.get_summary_and_reset()
    pdata.append_emotion_summary(0, spans_intro)
    pdata.append_timeline(f"Emotions detected: {_format_emotion_summary(spans_intro)}")
    pdata.append_timeline(f'Robot done speaking (intro) said "{intro_text}"') 

    # ── 10) Chat-state scaffolding ────────────────────────────────────────────
    completed_set: set[Tuple[str, int]] = set()
    prev_turn_json: Dict[str, str] = {
        "strategy": "No strategy decided yet",
        "message": "Hey there! I’m ClueBot—your friendly crossword side-kick. I can see which clue you’re working on and I’ll jump in with hints, fun facts, or just a bit of banter whenever you like. If my mouth lamp is glowing green, I’m listening! Ready when you are—good luck, and let’s crack this puzzle together!",
    }

    try:
        while True:
            # 1) Speech state & idle
            idle_sec = int(time.time() - transcriber.last_activity)
            if idle_sec == 0 and not in_speech:
                in_speech = True
                speaking_turn = turn_idx + 1 
                spans_before = emotion_detector.get_summary_and_reset()
                pdata.append_emotion_summary(speaking_turn, spans_before) 
                pdata.append_timeline(f"Emotions detected: {_format_emotion_summary(spans_before)}")
                pdata.append_timeline("User started speaking")
            if idle_sec > 0 and in_speech:
                in_speech = False 
            if idle_sec != prev_idle_log:
                prev_idle_log = idle_sec
                print(f"[IDLE] {idle_sec:2d}s since last speech", end="\r")

            # 2) Final user utterance (or idle injection)
            try:
                user_input = transcriber.transcription_queue.get(timeout=STT_POLL_SECS)
            except queue.Empty:
                user_input = None 
            if user_input is None and idle_sec >= IDLE_TIMEOUT:
                print("\n[MAIN] idle → injecting [[IDLE]]") 
                user_input = "[[IDLE]]" 
                transcriber.last_activity = time.time()  
            if user_input is None:
                continue  
            if user_input.lower().strip() == "quit":
                break  

            # 3) Seal user turn + emotions
            turn_idx += 1 
            spans_after_user = emotion_detector.get_summary_and_reset() 
            user_emotion = _predominant_emotion(spans_after_user)  
            pdata.append_emotion_summary(turn_idx, spans_after_user)  
            pdata.append_timeline(f"Emotions detected: {_format_emotion_summary(spans_after_user)}") 
            pdata.append_timeline(f'User done speaking said "{user_input}"') 

            # 4) Snapshot game state
            state_ready.clear()  
            socketio.emit("request_state")  
            if not state_ready.wait(timeout=0.4):
                print("[MAIN] ⚠️ snapshot timeout – stale state") 
            crossword_state = game_state.serialize()

            # Compute newly completed clues
            recently_completed = _compute_recently_completed(crossword_state, completed_set) 

            # 5) Build system prompt inputs (emotion from previous robot response)
            try:
                if not crossword_state:
                    raise KeyError 
                recent_spans = emotion_detector.fetch_pending_recent() 
                reaction_label = _predominant_emotion(recent_spans or []) if recent_spans else None

                system_msg_text = create_system_prompt(
                    game_state=crossword_state,
                    idle_seconds=idle_sec,
                    recently_completed=recently_completed,
                    user_emotion=reaction_label,  
                    last_user_utterance=user_input,
                    last_bot_message=prev_turn_json.get("message", "—"),
                    prev_strategy_notes=[prev_turn_json.get("strategy", "—")],
                )
            except KeyError:
                for link in get_server_links():  
                    print("   •", link)  
                system_msg_text = "### ROLE\ncrossword puzzle not yet connected."

            # 6) Call LLM (JSON: strategy + message)
            messages = (
                [{"role": "developer", "content": system_msg_text}]
                + history
                + [{"role": "user", "content": user_input}]
            )
            client = OpenAI(api_key=OPENAI_API_KEY)
            assistant_raw = client.chat.completions.create(
                model="gpt-4.1-2025-04-14",
                messages=messages,
            ).choices[0].message.content
            print(f"\n[MAIN] LLM response:\n{assistant_raw}\n")  

            try:
                parsed = json.loads(assistant_raw) 
                assistant_msg = parsed.get("message", "").strip() 
                prev_turn_json = parsed 
            except json.JSONDecodeError:
                print("[WARN] Assistant response was not valid JSON – using raw text.") 
                assistant_msg = assistant_raw.strip()
                prev_turn_json = {
                    "strategy": prev_turn_json.get("strategy", "(unknown)"),
                    "message": assistant_msg,
                }  

            # 7) Persist logs & history
            pdata.append_chat_turn(
                turn_idx,
                system_msg_text,
                assistant_msg,
                extra={"user_input": user_input, "assistant_raw": assistant_raw},
                user_emotion=reaction_label,
                recent_spans=recent_spans,
            ) 
            history.extend(
                [{"role": "user", "content": user_input},
                 {"role": "assistant", "content": assistant_raw}]
            ) 
            # 8) Speak the assistant
            pdata.append_timeline("Robot starts speaking")  
            transcriber.pause_listening()  
            _loop.run_until_complete(tts_manager.speak_text(assistant_msg))  
            transcriber.resume_listening()  
            pdata.append_timeline(f'Robot done speaking said "{assistant_msg}"') 

            # 9) Post-speech emotions & schedule recent summary
            spans_after_robot = emotion_detector.get_summary_and_reset() 
            pdata.append_emotion_summary(turn_idx, spans_after_robot) 
            pdata.append_timeline(
                f"Emotions detected: {_format_emotion_summary(spans_after_robot)}"
            )
            pdata.append_timeline(f'Robot done speaking said "{assistant_msg}"')

            emotion_detector.request_recent_summary(wait_sec=2.0, window_sec=5.0)

            # 10) Housekeeping
            _drain_transcription_queue(transcriber.transcription_queue)  
            transcriber.last_activity = time.time()
            prev_idle_log = -1 


    except KeyboardInterrupt:
        print("\n[MAIN] exiting …")
    finally:
        cam_stream.stop()
        audio_stream.stop()
        if USE_ROBOT:
            _loop.run_until_complete(tts_manager.close_robot())
        _loop.close()
        cv2.destroyAllWindows()
