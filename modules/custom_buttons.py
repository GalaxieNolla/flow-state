from PIL import Image, ImageTk
import tkinter as tk
from visuals import styles
import os

def create_mode_button(canvas, x, y, text, command):
    visuals_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "visuals")
    
    # Load and convert images for Tkinter
    active = os.path.join(visuals_dir, "active.jpg")
    inactive = os.path.join(visuals_dir, "inactive.jpg")
    
    inactive_i = ImageTk.PhotoImage(Image.open(inactive).convert("RGBA"))
    active_i = ImageTk.PhotoImage(Image.open(active).convert("RGBA"))

    # Canvas + label
    bg_id = canvas.create_image(x, y, image=inactive_i, anchor="center")
    text_label = tk.Label(canvas.master, text=text, fg="white", 
                          font=("Helvetica", 11, "bold"), 
                          bg=style.BG_DARK,
                          bd=0, cursor="hand2")
    canvas.create_window(x, y, window=text_label)

    def on_hover(e):
        canvas.itemconfig(bg_id, image=active_i)
        text_label.config(fg=styles.PURPLE_GLOW)

    def on_leave(e):
        canvas.itemconfig(bg_id, image=inactive_i)
        text_label.config(fg=styles.PURPLE_GLOW)

    text_label.bind("<Button-1>", lambda e: command())
    text_label.bind("<Enter>", on_hover)
    text_label.bind("<Leave>", on_leave)
    
    text_label.active_ = active_i
    text_label.inactive_i= inactive_i
    
    return text_label
