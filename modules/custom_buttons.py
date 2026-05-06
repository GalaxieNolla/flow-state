import os
import tkinter as tk
from PIL import Image, ImageTk
from visuals import styles

def create_mode_button(canvas, x, y, text, command, width, height):
    visuals_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "visuals", "images")

    active_pil  = Image.open(os.path.join(visuals_dir, "active.png")).convert("RGBA")
    inactive_pil = Image.open(os.path.join(visuals_dir, "inactive.png")).convert("RGBA")

    size_act = (width, height)
    size_in = (width - 110, height - 50)
    current_size = [width - 110, height - 50]

    inactive_i = ImageTk.PhotoImage(inactive_pil.resize(size_in, Image.Resampling.LANCZOS))
    active_i   = ImageTk.PhotoImage(active_pil.resize(size_act, Image.Resampling.LANCZOS))

    bg_id   = canvas.create_image(x, y, image=inactive_i, anchor="center")
    text_id = canvas.create_text(x, y, text=text, fill="white",
                                 font=("Cinzel", 30, "bold"), justify="center")

    tag = f"btn_{x}_{y}"
    canvas.addtag_withtag(tag, bg_id)
    canvas.addtag_withtag(tag, text_id)

    if not hasattr(canvas, '_btn_refs'):
        canvas._btn_refs = {}
    if not hasattr(canvas, 'all_refs'):
        canvas.all_refs = []

    canvas.all_refs.extend([active_i, inactive_i])

    def on_hover(e):
        w_px, h_px = current_size
        scaled_active = ImageTk.PhotoImage(
            active_pil.resize((w_px, h_px), Image.Resampling.LANCZOS)
        )
        canvas.itemconfig(bg_id, image=scaled_active)
        canvas.itemconfig(text_id, fill="white")
        canvas._btn_refs[bg_id] = scaled_active

    def on_leave(e):
        w_px, h_px = current_size
        scaled_inactive = ImageTk.PhotoImage(
            inactive_pil.resize((w_px, h_px), Image.Resampling.LANCZOS)
        )
        canvas.itemconfig(bg_id, image=scaled_inactive)
        canvas.itemconfig(text_id, fill="white")
        canvas._btn_refs[bg_id] = scaled_inactive

    canvas.tag_bind(tag, "<Button-1>", lambda e: command())
    canvas.tag_bind(tag, "<Enter>", on_hover)
    canvas.tag_bind(tag, "<Leave>", on_leave)

    return bg_id, text_id, active_pil, inactive_pil, size_act, current_size
