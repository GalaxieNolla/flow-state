from PIL import Image, ImageTk
import tkinter as tk
from visuals import styles
import os

def create_mode_button(canvas, x, y, text, command):
    visuals_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "visuals")
    size = (260, 90)
    
    active_path = os.path.join(visuals_dir, "active.png")
    inactive_path = os.path.join(visuals_dir, "inactive.png")
    
    inactive_i = ImageTk.PhotoImage(Image.open(inactive_path).convert("RGBA").resize(size, Image.Resampling.LANCZOS))
    active_i = ImageTk.PhotoImage(Image.open(active_path).convert("RGBA").resize(size))

    # create image, below text
    bg_id = canvas.create_image(x, y, image=inactive_i, anchor="center")
    
    # create label 2nd
    text_label = tk.Label(canvas.master, text=text, fg="white", 
                          font=("Helvetica", 11, "bold"), bd=0, cursor="hand2")
    
    canvas.create_window(x, y, window=text_label)

    def on_hover(e):
        nonlocal bg_id
        canvas.itemconfig(bg_id, image=active_i)
        text_label.config(fg=styles.PURPLE_GLOW)

    def on_leave(e):
        nonlocal bg_id
        canvas.itemconfig(bg_id, image=inactive_i)
        text_label.config(fg="white")

    text_label.bind("<Button-1>", lambda e: command())
    text_label.bind("<Enter>", on_hover)
    text_label.bind("<Leave>", on_leave)
    
    # keep ref so iamages don't disappear
    text_label.active_ref = active_i
    text_label.inactive_ref = inactive_i
    
    return text_label
