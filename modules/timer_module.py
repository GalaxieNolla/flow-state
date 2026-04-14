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
        
        # Create persistent clock text on the canvas
        self.clock_display = self.canvas.create_text(256, 256, text="", 
                                                     font=("Helvetica", 48, "bold"), 
                                                     fill=styles.PURPLE_GLOW, state="hidden")

    def show_setup(self):
        """Displays centered input for minutes."""
        self.status_label.pack_forget()
        self.canvas.delete("timer_ring")
        self.canvas.delete("timer_graphic")
        self.canvas.itemconfig(self.clock_display, state="hidden")
        
        # Create input frame on ROOT to ensure it sits above the canvas
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

    def create_center_graphic(self):
        """Processes monkey.jpg with a circular mask and transparency."""
        try:
            # Load and convert to RGBA
            img = Image.open("visuals/monkey.jpg").convert("RGBA")
            size = (200, 200)
            img = img.resize(size)

            # Create circular mask
            mask = Image.new("L", size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, size[0], size[1]), fill=255)
            
            # Apply mask and set transparency (0-255)
            img.putalpha(80) 
            
            # Combine image with mask
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
            self.input_frame.destroy()
            self.canvas.itemconfig(self.clock_display, state="normal")
            self.start(study_mins=mins)
        except ValueError:
            self.time_entry.config(fg="red")

    def start(self, study_mins=25, break_mins=5):
        self.total_seconds = study_mins * 60
        self.seconds_left = self.total_seconds
        self.tick(break_mins)

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
        """Draws the shadow graphic, ring, and clock text in order"""
        extent = (self.seconds_left / self.total_seconds) * 359.9
        self.canvas.delete("timer_ring")
        self.canvas.delete("timer_graphic")
        
        if not hasattr(self, 'center_image'):
            self.create_center_graphic()
        
        if hasattr(self, 'center_image'):
            self.canvas.create_image(256, 256, image=self.center_image, tags="timer_graphic")
            
        self.canvas.create_arc(156, 156, 356, 356, 
                               start=90, extent=extent, 
                               outline=styles.PURPLE_GLOW, width=8, 
                               style="arc", tags="timer_ring")
        self.canvas.tag_raise(self.clock_display)

    def handle_break(self, break_mins):
        self.canvas.itemconfig(self.clock_display, fill=styles.CYAN_FOG)
        self.seconds_left = break_mins * 60
        self.total_seconds = break_mins * 60
        self.root.after(3000, lambda: self.tick(break_mins))
