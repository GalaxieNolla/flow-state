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

    def create_ghost_monkey(self):
        """Creates a semi-transparent, blended graphic."""
        try:
            # 1. Load and force into RGBA for real transparency
            img = Image.open("visuals/monkey.jpg").convert("RGBA")
            size = (206, 206)
            img = img.resize(size, Image.Resampling.LANCZOS)

            # 2. Make it truly transparent
            # This loops through the image and lowers the 'Alpha' channel
            # to 15% so it's faint and ghostly
            alpha = img.getchannel('A')
            new_alpha = alpha.point(lambda p: p * 0.15) 
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
            self.canvas.itemconfig(self.clock_display, state="normal")
            self.start_timer(self.original_study_seconds)
        except ValueError:
            self.time_entry.config(fg="red")

    def start_timer(self, total_secs):
        self.total_seconds = total_secs
        self.seconds_left = total_secs
        # Only draw the heavy background layer once at the start of the round
        self.setup_background_layer()
        self.tick()

    def setup_background_layer(self):
        """Draws the static background elements ONLY ONCE to stop choppiness."""
        self.canvas.delete("timer_bg")
        
        # Subtle dark circular backing (stops numbers from getting lost)
        # We use a hex that matches your sky's dark tones
        self.canvas.create_oval(
            150, 150, 362, 362, 
            fill="#0b0514", outline="", 
            tags=("timer_bg", "timer_elements")
        )
        
        if not self.center_image:
            self.create_ghost_monkey()
        if self.center_image:
            self.canvas.create_image(
                256, 256, image=self.center_image, 
                tags=("timer_bg", "timer_elements")
            )

    def tick(self):
        if self.seconds_left >= 0:
            mins, secs = divmod(self.seconds_left, 60)
            self.canvas.itemconfig(self.clock_display, text=f"{mins:02d}:{secs:02d}")
            
            # Update ONLY the simple line ring every second (maximum performance)
            self.update_ring()
            
            self.seconds_left -= 1
            self.root.after(1000, self.tick)
        else:
            self.handle_cycle()

    def update_ring(self):
        """Only moves the arc; doesn't touch the heavy image layer."""
        extent = (self.seconds_left / self.total_seconds) * 359.9
        self.canvas.delete("timer_ring")
        self.canvas.create_arc(
            156, 156, 356, 356, start=90, extent=extent,
            outline=styles.PURPLE_GLOW if not self.is_break else "#00ffff",
            width=8, style="arc", tags=("timer_ring", "timer_elements")
        )
        self.canvas.tag_raise(self.clock_display)

    def handle_cycle(self):
        """Seamlessly transitions between Focus and Break."""
        self.is_break = not self.is_break
        next_time = 300 if self.is_break else self.original_study_seconds
        
        # Shift clock color for the break round
        color = "#00ffff" if self.is_break else styles.PURPLE_GLOW
        self.canvas.itemconfig(self.clock_display, fill=color)
        
        self.start_timer(next_time)
