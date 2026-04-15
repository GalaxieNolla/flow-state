import json
import os
import time
from datetime import datetime

SESSIONS_FILE = os.path.join(os.path.dirname(__file__), "sessions.json")

class SessionTracker:
    def __init__(self, monitor, nudge):
        self.monitor = monitor
        self.nudge = nudge
        self.session_start = time.time()
        self.distractions = 0
        self._was_distracted = False
        self._idle_check_job = None

    def start(self, root):
        self.root = root
        self._poll_idle()

    def record_distraction(self):
        self.distractions += 1

    def _poll_idle(self):
        try:
            idle = self.monitor.get_idle_time()
            if idle > 1800:  # 30 min idle
                self.save_session()
                self.session_start = time.time()
                self.distractions = 0
        except:
            pass
        self._idle_check_job = self.root.after(60_000, self._poll_idle)

    def save_session(self):
        duration_hrs = round(self.seconds_elapsed / 3600, 1)
        
        streak_mins = int((time.time() - self.nudge.streak_start) / 60)
        score = self._calculate_score(duration_mins, streak_mins, self.distractions)

        session = {
            "date": datetime.now().strftime("%b %d, %Y"),
            "duration_hrs": duration_hrs,
            "longest_streak": streak_mins,
            "distractions": self.distractions,
            "score": score
        }

        sessions = self._load_all()
        sessions.append(session)
        sessions.sort(key=lambda s: s["score"], reverse=True)

        with open(SESSIONS_FILE, "w") as f:
            json.dump(sessions, f, indent=2)

    def _calculate_score(self, duration, streak, distractions):
        return max(0, (duration * 2) + (streak * 3) - (distractions * 5))

    def _load_all(self):
        if not os.path.exists(SESSIONS_FILE):
            return []
        with open(SESSIONS_FILE, "r") as f:
            return json.load(f)
