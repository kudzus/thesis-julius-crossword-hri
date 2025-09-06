# robot_speech_tracker.py
import threading
from collections import deque
from difflib import SequenceMatcher

class RobotSpeechTracker:
    """
    Keeps the list of words the robot is *currently* speaking.
    Call .set(words) before playback, .clear() when playback ends.
    """
    def __init__(self, max_words=80):
        self._lock = threading.Lock()
        self._words = deque(maxlen=max_words)

    # ---------- robot‑side ---------- #
    def set(self, words):
        with self._lock:
            self._words.clear()
            self._words.extend(words)

    def clear(self):
        with self._lock:
            self._words.clear()

    # ---------- stt‑side ------------ #
    def copy(self):
        with self._lock:
            return list(self._words)

    # fuzzy helper
    @staticmethod
    def _similar(a, b, thresh=0.85):
        return SequenceMatcher(None, a, b).ratio() >= thresh

    def strip_from(self, user_words, fuzzy=False):
        """
        Remove *contiguous* chunks that equal the stored robot words.
        If fuzzy=True use SequenceMatcher on each pair.
        """
        print("User wrods:")
        print(user_words)
        
        robot_words = self.copy()
        print(robot_words)
        if not robot_words:
            return user_words                       # nothing to remove

        out, i = [], 0
        m, n = len(user_words), len(robot_words)

        while i < m:
            window = user_words[i:i+n]
            if len(window) == n and all(
                (w1 == w2) or (fuzzy and self._similar(w1, w2))
                for w1, w2 in zip(window, robot_words)
            ):
                i += n                              # skip the whole chunk
            else:
                out.append(user_words[i])
                i += 1
        print(out)
        return out