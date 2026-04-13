import tkinter as tk

class StudyTimer:
    def __init__(self, root, status_label):
        self.root = root
        self.status_label = status_label
        self.seconds_left = 0
        self.is_break = False

    def start(self, study_mins=25, break_mins=5):
        self.is_break = False
        self.seconds_left = study_mins * 60
        self.tick(break_mins)

    def tick(self, break_mins):
        mins, secs = divmod(self.seconds_left, 60)
        self.status_label.config(text=f"{mins:02d}:{secs:02d} ⚡")

        if self.seconds_left > 0:
            self.seconds_left -= 1
            self.root.after(1000, lambda: self.tick(break_mins))
        else:
            if not self.is_break:
                self.status_label.config(text="Break time! ☕", fg="#00ff73")
                self.seconds_left = break_mins * 60
                self.is_break = True
                self.root.after(2000, lambda: self.tick(break_mins))
            else:
                self.status_label.config(text="Back to studying! 💎", fg="#40c9c9")
                self.start() # Loops back to study
