import tkinter as tk
from visuals import styles

def create_mode_button(parent, text, command):
    """
    Creates a standardized button for the header area.
    Follows the visual theme defined in visuals/styles.py.
    """
    btn = tk.Button(
        parent, 
        text=text, 
        width=12, 
        command=command,
        # Uses the dark purple from your styles
        bg=styles.BG_DARK, 
        fg="white", 
        # Adds the muted grey border for a clean look
        highlightbackground=styles.GREY_MUTED, 
        highlightthickness=1,
        bd=0,
        # Ensures it looks good when clicked on macOS
        activebackground=styles.PURPLE_GLOW,
        activeforeground="white"
    )
    return btn
