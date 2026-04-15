# Colors
# BG_DARK = "#110820"     # Shadow color
# PURPLE_GLOW = "#c37aff" # neon purple
# CYAN_FOG = "#40c9c9"    # secondary teal/cyan
# GREY_MUTED = "#7a7a7a"  # Inactive text
# RED_LOCKIN = "#ff4b4b"  # Distractions
# PURPLE_BUTTON = "#2A1440" 

BG_DARK = "#0a0612"         # deeper, richer black-purple
PURPLE_GLOW = "#c084fc"     # softer arcane purple
PURPLE_DIM = "#7c3aed"      # deeper violet
GOLD_ACCENT = "#c9a84c"     # hex/piltover gold
CYAN_FOG = "#67e8f9"        # shimmer teal
GREY_MUTED = "#6b6080"      # muted with purple undertone
RED_LOCKIN = "#f87171"      # softer red
PURPLE_BUTTON = "#1e0f35"
RUNE_GLOW = "#a78bfa"       # lavender rune color
GOLD_ACCENT = "#c9a84c"
PURPLE_DIM = "#7c3aed"

# Leadership board
JINX_BLUE = "#5ee7ff"      # electric blue
JINX_BLUE_MID = "#7dd3fc"  # sky blue
JINX_BLUE_DARK = "#4a7fa5" # muted blue 
JINX_BG = "#050d1a"        # dark navy -- main background color
JINX_DIVIDER = "#1e3a5f"   # mid navy

# Font Styles
FONT_HEADER = ("Cinzel", 14)
FONT_DISPLAY = ("Cinzel", 40, "bold")
FONT_STATUS = ("Cinzel", 12, "italic")
FONT_FOOTER = ("Cormorant Garamond", 10, "italic") # easier to read, smaller
FONT_RUNE = ("Cormorant Garamond", 9, "italic")

def apply_ghost_style(label, command=None):
    """Applies the invisible/ghost style to any label to make it act like a button."""
    label.config(bg=BG_DARK, fg=GREY_MUTED, cursor="hand2")
    
    if command:
        label.bind("<Button-1>", lambda e: command())
    
    label.bind("<Enter>", lambda e: label.config(fg=PURPLE_GLOW))
    label.bind("<Leave>", lambda e: label.config(fg=GREY_MUTED))
