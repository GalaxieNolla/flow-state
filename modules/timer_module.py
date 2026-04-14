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

        self.clock_display = self.canvas.create_text(
            256, 256, text="", 
            font=("Helvetica", 48, "bold"), 
            fill=styles.PURPLE_GLOW, 
            state="hidden"
        )

    def show_setup(self):
        """Resets the UI for a new input session."""
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
        """Strips the black background and forces transparency."""
        try:
            img = Image.open("visuals/monkey.jpg").convert("RGBA")
            img = img.resize((200, 200), Image.Resampling.LANCZOS)
            
            # THE FIX: Replace black pixels with transparency
            datas = img.getdata()
            newData = []
            for item in datas:
                # If pixel is dark (black background), make it 100% transparent
                if item[0] < 40 and item[1] < 40 and item[2] < 40:
                    newData.append((0, 0, 0, 0))
                else:
                    # Keep the purple lines but make them semi-transparent 'ghostly'
                    newData.append((item[0], item[1], item[2], 100)) 
            
            img.putdata(newData)
            self.center_image = ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Image Error: {e}")

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
        self.setup_visuals()
        self.tick()

    def setup_visuals(self):
        """Draws static layers once to prevent choppiness."""
        self.canvas.delete("timer_bg")
        
        # FIX CHUNKY CIRCLE: Shrink dimensions (165,165 to 347,347) so it stays INSIDE the ring
        self.canvas.create_oval(
            165, 165, 347, 347, 
            fill="#0b0514", outline="", 
            tags=("timer_bg", "timer_elements")
        )
        
        if not self.center_image:
            self.create_transparent_monkey()
        if self.center_image:
            self.canvas.create_image(256, 256, image=self.center_image, tags=("timer_bg", "timer_elements"))

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
        """Smoothly updates the arc without redrawing images."""
        extent = (self.seconds_left / self.total_seconds) * 359.9
        self.canvas.delete("timer_ring")
        self.canvas.create_arc(
            156, 156, 356, 356, start=90, extent=extent,
            outline=styles.PURPLE_GLOW if not self.is_break else "#00ffff",
            width=8, style="arc", tags=("timer_ring", "timer_elements")
        )
        self.canvas.tag_raise(self.clock_display)

    def handle_cycle(self):
        """Swaps Focus and Break modes seamlessly."""
        self.is_break = not self.is_break
        next_time = 300 if self.is_break else self.original_study_seconds
        self.canvas.itemconfig(self.clock_display, fill="#00ffff" if self.is_break else styles.PURPLE_GLOW)
        self.start_timer(next_time)
