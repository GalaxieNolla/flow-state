import tkinter as tk
from visuals import styles

def create_mode_button(parent, text, command):
    """
    Creates a standardized button that follows your visual theme.
    Handles the transparent purple active state on macOS.
    """
    # A slightly lighter purple/fog color to make it look active but integrated
    active_purple = "#2A1440" 

    btn = tk.Button(
        parent, 
        text=text, 
        width=12, 
        command=command,
        bg=styles.BG_DARK, 
        fg="white", 
        highlightbackground=styles.GREY_MUTED, 
        highlightthickness=1,
        bd=0,
        # THE FIXES -------
        activebackground=active_purple,   # The transparent purple box you wanted
        activeforeground=styles.PURPLE_GLOW # The text turns primary purple
    )
    return btn
