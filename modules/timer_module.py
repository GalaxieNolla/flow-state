import tkinter as tk
from visuals import styles

class StudyTimer:
    def __init__(self, root, status_label, container, canvas):
        self.root = root
        self.canvas = canvas
        self.container = container 
        self.seconds_left = 0
        self.total_seconds = 0
        
        # This creates the text item directly on the background
        self.clock_display = self.canvas.create_text(256, 256, text="", 
                                                     font=("Helvetica", 48, "bold"), 
                                                     fill="#6b3fa0", state="hidden")

    def show_setup(self):
        self.canvas.delete("timer_ring")
        self.canvas.itemconfig(self.clock_display, state="hidden")
        
        # Create input frame on the ROOT so it sits ABOVE the canvas
        self.input_frame = tk.Frame(self.root, bg=styles.BG_DARK)
        self.input_frame.place(relx=0.5, rely=0.5, anchor="center")

        self.time_entry = tk.Entry(self.input_frame, font=styles.FONT_DISPLAY, 
                                   bg=styles.BG_DARK, fg=styles.PURPLE_GLOW, bd=0, 
                                   justify="center", insertbackground="white", width=4)
        self.time_entry.pack(side="top")
        
        line = tk.Frame(self.input_frame, height=2, bg=styles.PURPLE_GLOW)
        line.pack(fill="x", pady=2)

        self.time_entry.focus_set()
        self.time_entry.bind("<Return>", lambda e: self.validate_and_start())

    def validate_and_start(self):
        try:
            mins = int(self.time_entry.get())
            self.input_frame.destroy()
            self.canvas.itemconfig(self.clock_display, state="normal")
            self.start(study_mins=mins)
        except ValueError:
            self.time_entry.config(fg="red")

    def tick(self, break_mins):
        if self.seconds_left >= 0:
            mins, secs = divmod(self.seconds_left, 60)
            self.canvas.itemconfig(self.clock_display, text=f"{mins:02d}:{secs:02d}")
            self.draw_ring()
            self.seconds_left -= 1
            self.root.after(1000, lambda: self.tick(break_mins))
        else:
            self.handle_break(break_mins)

    def draw_ring(self):
        # Calculate arc based on time remaining
        extent = (self.seconds_left / self.total_seconds) * 359.9
        self.canvas.delete("timer_ring")
        self.canvas.create_oval(160, 160, 352, 352, fill="#0f071a", outline="") # shadow
        self.canvas.create_arc(156, 156, 356, 356, 
                               start=90, extent=extent, 
                               outline=styles.PURPLE_GLOW, width=8, 
                               style="arc", tags="timer_ring")
        self.canvas.tag_raise(self.clock_display)

    def start(self, study_mins=25, break_mins=5):
        self.total_seconds = study_mins * 60
        self.seconds_left = self.total_seconds
        self.tick(break_mins)

    def handle_break(self, break_mins):
        self.canvas.itemconfig(self.clock_display, fill=styles.CYAN_FOG)
        self.seconds_left = break_mins * 60
        self.total_seconds = break_mins * 60
        self.root.after(3000, lambda: self.tick(break_mins))
