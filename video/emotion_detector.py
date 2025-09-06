# video/emotion_detector.py
"""
EmotionDetector  – continuous background facial-emotion analysis.

Key public methods
──────────────────
start()                    – begin background polling.
get_summary_and_reset()    – return spans *since last reset* and clear them
                             (used for archival logging each turn).
get_recent_summary(sec)    – return spans that overlap the last <sec> seconds
                             WITHOUT clearing anything (useful for immediate
                             conversational context, e.g. “how did the user
                             look over the last 5 s?”).
stop()                     – clean shutdown at program exit.
"""

import threading
import time
from typing import List, Optional, Tuple

from ResidualMaskingNetwork.rmn import RMN


class EmotionDetector:
    # ─────────────────────────────────────────────────────────────────────
    def __init__(self, cam_stream, fps: int = 5, method: str = "RMN"):
        """
        Args:
          cam_stream: a CameraStream instance with .get_frame() → BGR array
          fps:        sampling rate (frames per second)
          method:     which detector to use; only "RMN" implemented
        """
        self.cam_stream = cam_stream
        self.fps = fps
        self.method = method.upper()
        self._pending_recent: Optional[List[Tuple[str, float]]] = None  # 🔶
        self._pending_lock  = threading.Lock()                          # 🔶
        self._pending_ready = threading.Event() 

        self._model = RMN() if self.method == "RMN" else None

        # --- data structures -------------------------------------------
        self._lock = threading.Lock()

        self.current_emotion: Optional[str] = None
        self._span_start: float = time.time()

        # Short-term buffer (cleared by get_summary_and_reset)
        self._emo_spans: List[Tuple[str, float]] = []  # (label, duration)

        # Session-long history (NEVER cleared)
        # list of (label, start_ts, end_ts)
        self._history_spans: List[Tuple[str, float, float]] = []

        # Thread bookkeeping
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    # ─────────────────────────────────────────────────────────────────────
    # Thread lifecycle
    # ─────────────────────────────────────────────────────────────────────
    def start(self) -> None:
        with self._lock:
            self._span_start = time.time()
            self.current_emotion = None
            self._emo_spans.clear()
            self._stop_event.clear()
            if not self._thread.is_alive():
                self._thread = threading.Thread(target=self._run, daemon=True)
                self._thread.start()

    def stop(self) -> None:
        if not self._stop_event.is_set():
            self._stop_event.set()
            self._thread.join()

    # ─────────────────────────────────────────────────────────────────────
    # Background loop
    # ─────────────────────────────────────────────────────────────────────
    def _run(self) -> None:
        period = 1.0 / self.fps
        last_ts = 0.0

        while not self._stop_event.is_set():
            frame = self.cam_stream.get_frame()
            if frame is None:
                time.sleep(0.01)
                continue

            now = time.time()
            if now - last_ts < period:
                time.sleep(0.005)
                continue
            last_ts = now

            label = self._detect_emotion(frame)

            if label != self.current_emotion:
                # close previous span
                if self.current_emotion is not None:
                    duration = round(now - self._span_start, 2)
                    with self._lock:
                        self._emo_spans.append((self.current_emotion, duration))
                        self._history_spans.append(
                            (self.current_emotion, self._span_start, now)
                        )
                # open new span
                self.current_emotion = label
                self._span_start = now

        # on shutdown: close final span
        now = time.time()
        if self.current_emotion is not None:
            duration = round(now - self._span_start, 2)
            with self._lock:
                self._emo_spans.append((self.current_emotion, duration))
                self._history_spans.append(
                    (self.current_emotion, self._span_start, now)
                )

    # ─────────────────────────────────────────────────────────────────────
    # Emotion inference helper
    # ─────────────────────────────────────────────────────────────────────
    def _detect_emotion(self, frame) -> str:
        if self._model is None:
            return "no-face"
        dets = self._model.detect_emotion_for_single_frame(frame)
        return dets[0]["emo_label"] if dets else "no-face"

    # ─────────────────────────────────────────────────────────────────────
    # Public API – long-term logging
    # ─────────────────────────────────────────────────────────────────────
    def get_summary_and_reset(self) -> List[Tuple[str, float]]:
        """
        Return spans *since the last call* and clear the short buffer,
        but keep the session-long history intact.
        """
        now = time.time()
        with self._lock:
            if self.current_emotion is not None:
                # include the in-flight span up to 'now'
                dur = round(now - self._span_start, 2)
                self._emo_spans.append((self.current_emotion, dur))
                self._history_spans.append(
                    (self.current_emotion, self._span_start, now)
                )
                self._span_start = now

            summary = list(self._emo_spans)
            self._emo_spans.clear()
            return summary

        # ──────────────────────────────────────────────────────────────────
    # NEW ❶  – schedule a snapshot after <wait_sec>
    # ──────────────────────────────────────────────────────────────────
    def request_recent_summary(
        self, wait_sec: float, window_sec: float
    ) -> None:
        """
        In <wait_sec> seconds, gather a snapshot of the last <window_sec>
        seconds’ emotion and cache it.  Non-blocking.
        """
        def _collect():
            summary = self.get_recent_summary(window_sec)
            with self._pending_lock:
                self._pending_recent = summary
            self._pending_ready.set()

        # reset state and launch timer
        self._pending_ready.clear()
        t = threading.Timer(wait_sec, _collect)
        t.daemon = True
        t.start()

    # ──────────────────────────────────────────────────────────────────
    # NEW ❷  – fetch that cached snapshot
    # ──────────────────────────────────────────────────────────────────
    def fetch_pending_recent(self) -> Optional[List[Tuple[str, float]]]:
        """
        Return the snapshot produced by the most-recent
        request_recent_summary().  Once fetched, it is cleared.
        If not ready yet, returns None.
        """
        if not self._pending_ready.is_set():
            return None
        with self._pending_lock:
            data = self._pending_recent
            self._pending_recent = None
        self._pending_ready.clear()
        return data

    # ─────────────────────────────────────────────────────────────────────
    # Public API – sliding window (NO reset)
    # ─────────────────────────────────────────────────────────────────────
    def get_recent_summary(self, last_seconds: float) -> List[Tuple[str, float]]:
        now = time.time()
        cutoff = now - last_seconds
        result: List[Tuple[str, float]] = []

        with self._lock:
            # 1) traverse history backwards
            for label, start, end in reversed(self._history_spans):
                if end <= cutoff:
                    break
                overlap_start = max(start, cutoff)
                overlap = end - overlap_start
                rounded = round(overlap, 2)
                if rounded > 0:
                    result.append((label, rounded))

            # 2) include current open span
            if self.current_emotion is not None:
                overlap_start = max(self._span_start, cutoff)
                overlap = now - overlap_start
                rounded = round(overlap, 2)
                if rounded > 0:
                    result.append((self.current_emotion, rounded))

        result.reverse()
        return result

