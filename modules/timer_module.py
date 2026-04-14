import tkinter as tk
from visuals import styles

class StudyTimer:
    def __init__(self, root, status_label, container, canvas):
        self.root = root
        self.status_label = status_label
        self.container = container 
        self.canvas = canvas
        self.seconds_left = 0
        self.total_seconds = 0
        self.running = False
        self.input_frame = None
        self.is_break = False

    def show_setup(self):
        """Displays centered input field within the ring area."""
        self.status_label.pack_forget()
        self.canvas.delete("timer_ring")
        
        # Create a frame that centers itself in the container area
        self.input_frame = tk.Frame(self.container, bg=styles.BG_DARK)
        self.input_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Prompt
        prompt = tk.Label(self.input_frame, text="set minutes", 
                          font=styles.FONT_NORMAL, fg=styles.PURPLE_GLOW, bg=styles.BG_DARK)
        prompt.pack(side="top", pady=(0, 5))

        # Centered Entry field using the big display font
        self.time_entry = tk.Entry(self.input_frame, font=styles.FONT_DISPLAY, 
                                   bg=styles.BG_DARK, fg=styles.PURPLE_GLOW, bd=0, 
                                   justify="center", insertbackground="white",
                                   width=4)
        self.time_entry.pack(side="top")
        
        # Styled underline
        line = tk.Frame(self.input_frame, height=2, bg=styles.PURPLE_GLOW)
        line.pack(fill="x", pady=2)

        self.time_entry.focus_set()
        self.time_entry.bind("<Return>", lambda e: self.validate_and_start())

    def validate_and_start(self):
        """Transition from input to the actual countdown circle."""
        try:
            mins = int(self.time_entry.get())
            self.input_frame.destroy() 
            
            # Show big clock label in center
            self.status_label.pack(expand=True) 
            self.start(study_mins=mins)
        except ValueError:
            self.time_entry.config(fg="red")

    def start(self, study_mins=25, break_mins=5):
        self.running = True
        self.is_break = False
        self.total_seconds = study_mins * 60
        self.seconds_left = self.total_seconds
        self.tick(break_mins)

    def tick(self, break_mins):
        if self.seconds_left >= 0:
            mins, secs = divmod(self.seconds_left, 60)
            self.status_label.config(text=f"{mins:02d}:{secs:02d}", font=styles.FONT_DISPLAY)
            
            # Update the circular ring
            self.draw_ring()
            
            self.seconds_left -= 1
            self.root.after(1000, lambda: self.tick(break_mins))
        else:
            self.handle_break(break_mins)

    def draw_ring(self):
        """Calculates and draws the arc based on percentage of time left."""
        # 359.9 prevents the arc from disappearing at exactly 360
        extent = (self.seconds_left / self.total_seconds) * 359.9
        
        self.canvas.delete("timer_ring")
        # Centered at (256, 256) with a radius of 100px
        self.canvas.create_arc(156, 156, 356, 356, 
                               start=90, extent=extent, 
                               outline=styles.PURPLE_GLOW, width=8, 
                               style="arc", tags="timer_ring")

    def handle_break(self, break_mins):
        if not self.is_break:
            self.canvas.delete("timer_ring")
            self.status_label.config(text="BREAK TIME", fg=styles.CYAN_FOG, font=styles.FONT_STATUS)
            self.seconds_left = break_mins * 60
            self.total_seconds = break_mins * 60
            self.is_break = True
            self.root.after(3000, lambda: self.tick(break_mins))
        else:
            self.status_label.config(text="FOCUS", fg=styles.PURPLE_GLOW)
            self.running = False
