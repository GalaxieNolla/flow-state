import os
import tkinter as tk
from PIL import Image, ImageTk
from visuals import styles

def create_mode_button(canvas, x, y, text, command):
    visuals_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "visuals")
    size = (320, 100)
    
    active_path = os.path.join(visuals_dir, "active.png")
    inactive_path = os.path.join(visuals_dir, "inactive.png")

    inactive_i = ImageTk.PhotoImage(Image.open(inactive_path).convert("RGBA").resize(size, Image.Resampling.LANCZOS))
    active_i = ImageTk.PhotoImage(Image.open(active_path).convert("RGBA").resize(size, Image.Resampling.LANCZOS))

    bg_id = canvas.create_image(x, y, image=inactive_i, anchor="center")
    
    text_id = canvas.create_text(x, y, text=text, fill="white", font=("Helvetica", 25, "bold"), justify="center")

    def on_hover(e):
        canvas.itemconfig(bg_id, image=active_i)
        canvas.itemconfig(text_id, fill=styles.PURPLE_GLOW)

    def on_leave(e):
        canvas.itemconfig(bg_id, image=inactive_i)
        canvas.itemconfig(text_id, fill="white")

    canvas.tag_bind(bg_id, "<Button-1>", lambda e: command())
    canvas.tag_bind(text_id, "<Button-1>", lambda e: command())
    
    canvas.tag_bind(bg_id, "<Enter>", on_hover)
    canvas.tag_bind(text_id, "<Enter>", on_hover)
    canvas.tag_bind(bg_id, "<Leave>", on_leave)
    
    # Keep references
    if not hasattr(canvas, 'all_refs'):
        canvas.all_refs = []
    canvas.all_refs.extend([active_i, inactive_i])
    
    return bg_id
