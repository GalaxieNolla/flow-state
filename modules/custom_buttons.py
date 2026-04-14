import tkinter as tk
from visuals import styles

def create_mode_button(parent, text, command):
    # This color is the "active" purple fog
    active_bg = "#2A1440" 

    btn = tk.Label(
        parent, 
        text=text, 
        font=("Helvetica", 11, "bold"),
        width=15,          # Fixed width keeps it consistent
        height=1,          # Fixed height
        bg=styles.BG_DARK, 
        fg="white", 
        padx=10, 
        pady=5,
        cursor="hand2"
    )

    # Hover Effects
    btn.bind("<Enter>", lambda e: btn.config(bg=active_bg, fg=styles.PURPLE_GLOW))
    btn.bind("<Leave>", lambda e: btn.config(bg=styles.BG_DARK, fg="white"))
    
    # Click Logic
    btn.bind("<Button-1>", lambda e: command())

    return btn
