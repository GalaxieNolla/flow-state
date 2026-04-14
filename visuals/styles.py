# Colors
BG_DARK = "#110820"     # The deep shadow color
PURPLE_GLOW = "#c37aff" # Primary neon purple
CYAN_FOG = "#40c9c9"    # The secondary teal/cyan
GREY_MUTED = "#7a7a7a"  # For inactive text
RED_LOCKIN = "#ff4b4b"  # For distractions
active_purple = "#2A1440" 

# Font Styles
FONT_HEADER = ("Helvetica", 14)
FONT_DISPLAY = ("Helvetica", 40, "bold")
FONT_STATUS = ("Helvetica", 12, "italic")
FONT_FOOTER = ("Helvetica", 10, "italic")

def apply_ghost_style(label, command=None):
    """Applies the invisible/ghost style to any label to make it act like a button."""
    label.config(bg=BG_DARK, fg=GREY_MUTED, cursor="hand2")
    
    if command:
        label.bind("<Button-1>", lambda e: command())
    
    label.bind("<Enter>", lambda e: label.config(fg=PURPLE_GLOW))
    label.bind("<Leave>", lambda e: label.config(fg=GREY_MUTED))
