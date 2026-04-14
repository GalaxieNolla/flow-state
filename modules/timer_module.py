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

        # Create clock text once; keep it on top
        self.clock_display = self.canvas.create_text(
            256, 256, text="", 
            font=("Helvetica", 48, "bold"), 
            fill=styles.PURPLE_GLOW, 
            state="hidden"
        )

    def show_setup(self):
        """Resets UI and shows time input."""
        self.canvas.delete("timer_elements") # Clean start
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
        """Creates a truly transparent, circular graphic."""
        try:
            # 1. Load and resize
            img = Image.open("visuals/monkey.jpg").convert("RGBA")
            size = (206, 206)
            img = img.resize(size, Image.Resampling.LANCZOS)

            # 2. Create a circular mask with smooth edges
            mask = Image.new("L", size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, size[0], size[1]), fill=255)

            # 3. Apply global transparency (Adjust 60 lower for more 'ghostly')
            alpha = img.split()[3]
            alpha = alpha.point(lambda p: p * 0.25) # 25% opacity
            img.putalpha(alpha)

            # 4. Final composite with the mask
            output = Image.new("RGBA", size, (0, 0, 0, 0))
            output.paste(img, (0, 0), mask=mask)

            self.center_image = ImageTk.PhotoImage(output)
        except Exception as e:
            print(f"Image error: {e}")

    def validate_and_start(self):
        try:
            mins = int(self.time_entry.get())
            self.original_study_seconds = mins * 60
            self.input_frame.destroy()
            self.canvas.itemconfig(self.clock_display, state="normal", fill=styles.PURPLE_GLOW)
            self.start_timer(mins * 60)
        except ValueError:
            self.time_entry.config(fg="red")

    def start_timer(self, total_secs):
        self.total_seconds = total_secs
        self.seconds_left = total_secs
        self.tick()

    def tick(self):
        if self.seconds_left >= 0:
            mins, secs = divmod(self.seconds_left, 60)
            self.canvas.itemconfig(self.clock_display, text=f"{mins:02d}:{secs:02d}")
            self.update_visuals()
            self.seconds_left -= 1
            self.root.after(1000, self.tick)
        else:
            self.handle_cycle()

    def update_visuals(self):
        """Separates static and dynamic layers to fix choppiness."""
        # 1. Draw Static Background (Box + Monkey) ONLY ONCE
        if not self.canvas.find_withtag("timer_bg"):
            # Darkened back-plate for readability
            self.canvas.create_oval(150, 150, 362, 362, fill="#0b0514", outline="", tags=("timer_bg", "timer_elements"))
            
            if not self.center_image:
                self.create_transparent_monkey()
            if self.center_image:
                self.canvas.create_image(256, 256, image=self.center_image, tags=("timer_bg", "timer_elements"))

        # 2. Update Dynamic Ring
        extent = (self.seconds_left / self.total_seconds) * 359.9
        self.canvas.delete("timer_ring")
        self.canvas.create_arc(
            156, 156, 356, 356, start=90, extent=extent,
            outline=styles.PURPLE_GLOW if not self.is_break else "#00ffff",
            width=8, style="arc", tags=("timer_ring", "timer_elements")
        )
        self.canvas.tag_raise(self.clock_display)

    def handle_cycle(self):
        """Swaps between study and 5-min break."""
        self.is_break = not self.is_break
        next_time = 300 if self.is_break else self.original_study_seconds
        
        # Color shift for visual cue
        color = "#00ffff" if self.is_break else styles.PURPLE_GLOW
        self.canvas.itemconfig(self.clock_display, fill=color)
        
        self.start_timer(next_time)
