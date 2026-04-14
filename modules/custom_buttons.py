import tkinter as tk
from visuals import styles

def create_mode_button(parent, text, command):
    """
    Creates a 'Ghost Button' using a Label to avoid the macOS 
    white-box glitch and allow for transparent purple styling.
    """
    # This color is a slightly lighter purple fog to act as a background
    active_bg = "#2A1440" 

    btn = tk.Label(
        parent, 
        text=text, 
        font=("Helvetica", 12, "bold"),
        width=15, 
        bg=styles.BG_DARK, 
        fg="white", 
        padx=10, 
        pady=5,
        cursor="hand2" # Makes it feel clickable
    )

    # Hover Effects (Visual feedback)
    btn.bind("<Enter>", lambda e: btn.config(bg=active_bg, fg=styles.PURPLE_GLOW))
    btn.bind("<Leave>", lambda e: btn.config(bg=styles.BG_DARK, fg="white"))
    
    # Click Logic (The actual button functionality)
    btn.bind("<Button-1>", lambda e: command())

    return btn
