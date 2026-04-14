import tkinter as tk
from visuals import styles
from PIL import Image, ImageTk, ImageDraw

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
        self.original_study_seconds = 0  # To remember Pomodoro rounds

        # Create persistent clock text
        self.clock_display = self.canvas.create_text(
            256, 256, text="", 
            font=("Helvetica", 48, "bold"), 
            fill=styles.PURPLE_GLOW, 
            state="hidden"
        )

    def show_setup(self):
        """Displays centered input for minutes."""
        self.status_label.pack_forget()
        self.canvas.delete("timer_ring")
        self.canvas.delete("timer_static")
        self.canvas.itemconfig(self.clock_display, state="hidden")
        
        self.input_frame = tk.Frame(self.root, bg=styles.BG_DARK)
        self.input_frame.place(relx=0.5, rely=0.5, anchor="center")

        self.time_entry = tk.Entry(
            self.input_frame, font=styles.FONT_DISPLAY, 
            bg=styles.BG_DARK, fg=styles.PURPLE_GLOW, bd=0, 
            justify="center", insertbackground="white", width=4
        )
        self.time_entry.pack(side="top")
        
        line = tk.Frame(self.input_frame, height=2, bg=styles.PURPLE_GLOW)
        line.pack(fill="x", pady=2)

        self.time_entry.focus_set()
        self.time_entry.bind("<Return>", lambda e: self.validate_and_start())

    def create_center_graphic(self):
        """Processes monkey.jpg with a circular mask and transparency."""
        try:
            img = Image.open("visuals/monkey.jpg").convert("RGBA")
            size = (200, 200)
            img = img.resize(size)

            mask = Image.new("L", size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, size[0], size[1]), fill=255)
            
            img.putalpha(80) 
            
            output = Image.new("RGBA", size, (0, 0, 0, 0))
            output.paste(img, (0, 0), mask=mask)

            self.center_image = ImageTk.PhotoImage(output)
            return self.center_image
        except Exception as e:
            print(f"Error loading monkey.jpg: {e}")
            return None

    def validate_and_start(self):
        try:
            mins = int(self.time_entry.get())
            self.original_study_seconds = mins * 60 # Store OG time for rounds
            self.input_frame.destroy()
            self.canvas.itemconfig(self.clock_display, state="normal")
            self.start(study_mins=mins)
        except ValueError:
            self.time_entry.
