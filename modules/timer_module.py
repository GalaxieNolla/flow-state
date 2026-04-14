import tkinter as tk
from visuals import styles

class StudyTimer:
    def __init__(self, root, status_label):
        self.root = root
        self.status_label = status_label
        self.seconds_left = 0
        self.running = False # no more flashing

    def start(self, study_mins=25, break_mins=5):
        self.running = True
        self.is_break = False
        self.seconds_left = study_mins * 60
        self.tick(break_mins)

    def tick(self, break_mins):
        if self.seconds_left >= 0:
            mins, secs = divmod(self.seconds_left, 60)
            # Big, clean timer font
            self.status_label.config(text=f"{mins:02d}:{secs:02d}", font=styles.FONT_DISPLAY)
            self.seconds_left -= 1
            self.root.after(1000, lambda: self.tick(break_mins))
        else:
            if not self.is_break:
                self.status_label.config(text="BREAK TIME", fg=styles.CYAN_FOG, font=styles.FONT_STATUS)
                self.seconds_left = break_mins * 60
                self.is_break = True
                self.root.after(3000, lambda: self.tick(break_mins))
            else:
                self.status_label.config(text="FOCUS", fg=styles.PURPLE_GLOW)
                self.running = False # app.py time
