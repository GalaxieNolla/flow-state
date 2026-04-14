import tkinter as tk
from visuals import styles

class StudyTimer:
    def __init__(self, root, status_label, container):
        self.root = root
        self.status_label = status_label
        self.container = container # The main window area
        self.seconds_left = 0
        self.running = False
        self.input_frame = None

    def show_setup(self):
        """Displays the input field instead of starting a clock."""
        self.status_label.pack_forget() # Hide clock initially
        
        self.input_frame = tk.Frame(self.container, bg=styles.BG_DARK)
        self.input_frame.pack(fill="x", pady=20)

        # Prompt using the alignment logic we perfected
        prompt = tk.Label(self.input_frame, text="set minutes:", 
                          font=styles.FONT_NORMAL, fg=styles.PURPLE_GLOW, bg=styles.BG_DARK)
        prompt.pack(side="left", padx=(15, 10))

        self.time_entry = tk.Entry(self.input_frame, font=styles.FONT_NORMAL, 
                                   bg=styles.BG_DARK, fg=styles.PURPLE_GLOW, bd=0, 
                                   insertbackground="white", highlightthickness=1, 
                                   highlightbackground=styles.PURPLE_GLOW)
        self.time_entry.pack(side="left", fill="x", expand=True, padx=(0, 15))
        self.time_entry.focus_set()

        # Start timer on Enter key
        self.time_entry.bind("<Return>", lambda e: self.validate_and_start())

    def validate_and_start(self):
        """Checks for a valid number and starts the countdown."""
        try:
            mins = int(self.time_entry.get())
            self.input_frame.destroy() # Clear input UI
            self.status_label.pack(expand=True, pady=40) # Show big clock
            self.start(study_mins=mins)
        except ValueError:
            self.time_entry.config(highlightbackground="red")

    def start(self, study_mins=25, break_mins=5):
        self.running = True
        self.is_break = False
        self.seconds_left = study_mins * 60
        self.tick(break_mins)

    def tick(self, break_mins):
        if self.seconds_left >= 0:
            mins, secs = divmod(self.seconds_left, 60)
            # Big display font for the countdown
            self.status_label.config(text=f"{mins:02d}:{secs:02d}", font=styles.FONT_DISPLAY)
            self.seconds_left -= 1
            self.root.after(1000, lambda: self.tick(break_mins))
        else:
            self.handle_break(break_mins)

    def handle_break(self, break_mins):
        if not self.is_break:
            self.status_label.config(text="BREAK TIME", fg=styles.CYAN_FOG, font=styles.FONT_STATUS)
            self.seconds_left = break_mins * 60
            self.is_break = True
            self.root.after(3000, lambda: self.tick(break_mins))
        else:
            self.status_label.config(text="FOCUS", fg=styles.PURPLE_GLOW)
            self.running = False
