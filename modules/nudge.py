import tkinter as tk
import time

class Nudge:
    def __init__(self, root):
        self.root = root
        self.window = None
        self.streak_start = time.time()
        self.streak_minutes = 0
        self.countdown = 0
        self.countdown_job = None
        self.is_distracted = False
        #ensures nudgei snot blippy
        self._last_shown = 0
        self._COOLDOWN = 3.0

    def show(self, site_name=""):
        self.is_distracted = True

        # update labels if window exists
        if self.window and self.window.winfo_exists():
            self._update_labels(site_name)
            return

        now = time.time()
        if now - self._last_shown < self._COOLDOWN:
            return
        self._last_shown = now

        if self.countdown == 0:
            self.countdown = 30

        sw = self.root.winfo_screenwidth()
        x = sw - 260
        self.window = tk.Toplevel(self.root)
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)

        self.window.attributes("-alpha", 0.92)  # slight transparency & no glitching out (hopefully)
        self.window.wm_attributes("-topmost", True)

        try:
            self.window.wm_attributes("-type", "notification")  # Linux/X11
        except tk.TclError:
            pass

        self.window.focus_set = lambda *a: None
        self.root.after(10, lambda: self.root.focus_force())

        self.window.geometry(f"240x120+{x}+20")
        self.window.configure(bg="#120921")

        tk.Label(self.window, text="🔥", font=("Helvetica", 20), bg="#120921").place(x=14, y=12)
        self.streak_label = tk.Label(self.window, text=self._streak_text(),
                                     font=("Helvetica", 11), bg="#120921", fg="#c37aff")
        self.streak_label.place(x=48, y=14)
        self.msg_label = tk.Label(self.window, text=f"hey, {site_name} isn't it...",
                                  font=("Helvetica", 10, "italic"), bg="#120921", fg="#ff6b6b",
                                  wraplength=210)
        self.msg_label.place(x=14, y=48)
        self.timer_label = tk.Label(self.window, text=f"{self.countdown}s to get back",
                                    font=("Helvetica", 10), bg="#120921", fg="#7a6a9a")
        self.timer_label.place(x=14, y=78)
        self._tick()

    def hide(self):
        self.is_distracted = False
        self.countdown = 0
        if self.countdown_job:
            self.root.after_cancel(self.countdown_job)
            self.countdown_job = None
        if self.window and self.window.winfo_exists():
            self.window.destroy()
            self.window = None
        self.streak_start = time.time()

    def reset_streak(self):
        self.streak_start = time.time()
        self.streak_minutes = 0

    def _streak_text(self):
        mins = int((time.time() - self.streak_start) / 60)
        return f"{mins} min focus streak"

    def _update_labels(self, site_name=""):
        if hasattr(self, 'streak_label') and self.streak_label.winfo_exists():
            self.streak_label.config(text=self._streak_text())
        if site_name and hasattr(self, 'msg_label') and self.msg_label.winfo_exists():
            self.msg_label.config(text=f"hey, {site_name} isn't it...")

    def _tick(self):
        if not self.window or not self.window.winfo_exists():
            return
        self.countdown -= 1
        if self.countdown <= 0:
            if hasattr(self, 'timer_label') and self.timer_label.winfo_exists():
                self.timer_label.config(text="streak reset!", fg="#ff4b4b")
            self.reset_streak()
            self.countdown_job = self.root.after(2000, self._close_after_reset)
        else:
            if hasattr(self, 'timer_label') and self.timer_label.winfo_exists():
                self.timer_label.config(text=f"{self.countdown}s to get back")
            self.countdown_job = self.root.after(1000, self._tick)

    def _close_after_reset(self):
        if self.window and self.window.winfo_exists():
            self.window.destroy()
            self.window = None
