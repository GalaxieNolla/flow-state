from PIL import Image, ImageDraw, ImageTk
import tkinter as tk
from visuals import styles

def create_mode_button(parent, text, command):
    # Create a small rounded rectangle image
    width, height = 150, 40
    radius = 20
    
    # Create mask for rounded corners
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((0, 0, width, height), radius=radius, fill="#2A1440", outline=styles.GREY_MUTED)
    
    btn_img = ImageTk.PhotoImage(img)
    
    # Create label with image as background
    btn = tk.Label(parent, text=text, image=btn_img, compound="center",
                   bg=styles.BG_DARK, fg="white", bd=0, cursor="hand2")
    btn.image = btn_img # Keep reference!
    
    btn.bind("<Button-1>", lambda e: command())
    return btn
