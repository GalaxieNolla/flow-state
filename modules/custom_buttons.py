import os
import tkinter as tk
from PIL import Image, ImageTk
from visuals import styles

def create_mode_button(canvas, x, y, text, command, width, height):
    visuals_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "visuals", "images")
    # e.g. size = (270, 90)
    size = (width, height)

    active_path = os.path.join(visuals_dir, "active.png")
    inactive_path = os.path.join(visuals_dir, "inactive.png")

    # Store the PIL images (not just PhotoImage) so we can resize on demand
    active_pil  = Image.open(active_path).convert("RGBA")
    inactive_pil = Image.open(inactive_path).convert("RGBA")

    inactive_i = ImageTk.PhotoImage(inactive_pil.resize(size, Image.Resampling.LANCZOS))
    active_i   = ImageTk.PhotoImage(active_pil.resize(size, Image.Resampling.LANCZOS))

    bg_id   = canvas.create_image(x, y, image=inactive_i, anchor="center")
    text_id = canvas.create_text(x, y, text=text, fill="white",
                                 font=("Cinzel", 24, "bold"), justify="center")

    tag = f"btn_{x}_{y}"
    canvas.addtag_withtag(tag, bg_id)
    canvas.addtag_withtag(tag, text_id)

    def on_hover(e):
        # Get current displayed size from the inactive image already on canvas
        cur_w = inactive_i.width()
        cur_h = inactive_i.height()
        scaled_active = ImageTk.PhotoImage(
            active_pil.resize((cur_w, cur_h), Image.Resampling.LANCZOS)
        )
        canvas.itemconfig(bg_id, image=scaled_active)
        canvas.itemconfig(text_id, fill=styles.PURPLE_GLOW)
        # Keep reference alive
        canvas._hover_ref = scaled_active

    def on_leave(e):
        cur_w = inactive_i.width()
        cur_h = inactive_i.height()
        scaled_inactive = ImageTk.PhotoImage(
            inactive_pil.resize((cur_w, cur_h), Image.Resampling.LANCZOS)
        )
        canvas.itemconfig(bg_id, image=scaled_inactive)
        canvas.itemconfig(text_id, fill="white")
        canvas._hover_ref = scaled_inactive

    canvas.tag_bind(tag, "<Button-1>", lambda e: command())
    canvas.tag_bind(tag, "<Enter>", on_hover)
    canvas.tag_bind(tag, "<Leave>", on_leave)

    if not hasattr(canvas, 'all_refs'):
        canvas.all_refs = []
    canvas.all_refs.extend([active_i, inactive_i])

    # Return all four things the caller needs to reposition + resize
    return bg_id, text_id, active_pil, inactive_pil, size #size as a tuple
