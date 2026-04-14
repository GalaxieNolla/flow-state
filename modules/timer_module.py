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
        self.is_break = False
        self.original_study_seconds = 0
        self.center_image = None

        # Create clock text ONCE; persistent and on top
        self.clock_display = self.canvas.create_text(
            256, 256, text="", 
            font=("Helvetica", 48, "bold"), 
            fill=styles.PURPLE_GLOW, 
            state="hidden"
        )

    def show_setup(self):
        """Clean UI reset."""
        self.canvas.delete("timer_elements") 
        self.canvas.itemconfig(self.clock_display, state="hidden")
        
        self.input_frame = tk.Frame(self.root, bg=styles.BG_DARK)
        self.input_frame.place(relx=0.5, rely=0.5, anchor="center")

        self.time_entry = tk.Entry(
            self.input_frame, font=styles.FONT_DISPLAY, 
            bg=styles.BG_DARK, fg=styles.PURPLE_GLOW, bd=0, 
            justify="center", insertbackground="white", width=4
        )
        self.time_entry.pack(side="top")
        
        tk.Frame(self.input_frame, height=2, bg=styles.PURPLE_GLOW).pack(fill="x", pady=2)
        self.time_entry.focus_set()
        self.time_entry.bind("<Return>", lambda e: self.validate_and_start())

    def create_transparent_monkey(self):
        """Creates a truly semi-transparent graphic."""
        try:
            # 1. Load and force into RGBA for real transparency
            img = Image.open("visuals/monkey.jpg").convert("RGBA")
            size = (206, 206)
            img = img.resize(size, Image.Resampling.LANCZOS)

            # 2. Create the 'ghost' effect by lowering the global Alpha channel
            # This makes the image 20% opaque so the background clouds show through
            alpha = img.getchannel('A')
            new_alpha = alpha.point(lambda p: p * 0.2) 
            img.putalpha(new_alpha)

            # 3. Apply circular crop
            mask = Image.new("L", size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, size[0], size[1]), fill=255)
            
            output = Image.new("RGBA", size, (0, 0, 0, 0))
            output.paste(img, (0, 0), mask=mask)

            self.center_image = ImageTk.PhotoImage(output)
        except Exception as e:
            print(f"Transparency Error: {e}")

    def validate_and_start(self):
        try:
            mins = int(self.time_entry.get())
            self.original_study_seconds = mins * 60
            self.input_frame.destroy()
            self.canvas.itemconfig(self.clock_display, state="normal", fill=styles.PURPLE_GLOW)
            self.start_timer(self.original_study_seconds)
        except ValueError:
            self.time_entry.config(fg="red")

    def start_timer(self, total_secs):
        self.total_seconds = total_secs
        self.seconds_left = total_secs
        # Create static BG elements once at the start of the round to save CPU
        self.setup_visual_layers()
        self.tick()

    def setup_visual_layers(self):
        """Draws the static background elements ONLY ONCE to stop choppiness."""
        self.canvas.delete("timer_bg")
        
        self.canvas.create_oval(
            150, 150, 362, 362, 
            fill="#0b0514", outline="", 
            tags=("timer_bg", "timer_elements")
        )
        
        if not self.center_image:
            self.create_transparent_monkey()
        if self.center_image:
            self.canvas.create_image(
                256, 256, image=self.center_image, 
                tags=("timer_bg", "timer_elements")
            )

    def tick(self):
        if self.seconds_left >= 0:
            mins, secs = divmod(self.seconds_left, 60)
            self.canvas.itemconfig(self.clock_display, text=f"{mins:02d}:{secs:02d}")
            
            self.update_ring()
            
            self.seconds_left -= 1
            self.root.after(1000, self.tick)
        else:
            self.handle_cycle()

    def update_ring(self):
        """Only moves the arc; doesn't touch the heavy images."""
