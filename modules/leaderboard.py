import tkinter as tk
import json
import os
from visuals import styles
from PIL import Image, ImageTk

SESSIONS_FILE = os.path.join(os.path.dirname(__file__), "sessions.json")

class Leaderboard:
    def __init__(self, root):
        self.root = root
        self.window = None
    
    def open(self):
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return

        self.window = tk.Toplevel(self.root)
        self.window.title("Leaderboard")
        self.window.configure(bg=styles.BG_DARK)
        self.window.attributes("-topmost", True)

        # background image
        img_path = os.path.join(os.path.dirname(__file__), "..", "visuals", "leader background.png")
        img = Image.open(img_path)
        img.thumbnail((380, 600), Image.Resampling.LANCZOS)
        self.bg_image = ImageTk.PhotoImage(img)
        self.canvas = tk.Canvas(self.window, width=img.width, height=img.height, highlightthickness=0)
        self.window.geometry(f"{img.width}x{img.height}")
        self.canvas.config(width=img.width, height=img.height)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")

        # remove content frame entirely
        self.canvas.create_text(img.width // 2, 50,
            text="✦ Hall of Focus ✦",
            font=("Cinzel", 18, "bold"), fill=styles.JINX_BLUE)
        
        self.canvas.create_text(img.width // 2, 85,
            text="BOOM! The Winner's Circle",
            font=("Cinzel", 11, "italic"), fill=styles.JINX_BLUE_MID)
        
        # semi-transparent box behind the table only
        self.canvas.create_rectangle(20, 105, img.width - 20, 400,
            fill=white, stipple="gray25",
            outline=white)
        
        # list frame still a widget but placed lower
        self.list_frame = tk.Frame(self.canvas, bg=styles.JINX_BG)
        self.canvas.create_window(img.width // 2, 115, window=self.list_frame, anchor="n")
        
        self._render_sessions()

        # clear button
        tk.Label(self.window, text="clear history", font=styles.FONT_FOOTER,
                 fg=styles.JINX_BLUE_DARK, bg=styles.JINX_BG, cursor="hand2").pack(pady=12)

    def _render_sessions(self):
        sessions = self._load()
    
        if not sessions:
            tk.Label(self.list_frame, text="nothing to see here...yet.\nback to the books, cupcake!",
                     font=("Cinzel", 13, "italic"),
                     fg=styles.JINX_BLUE_MID, bg=styles.JINX_BG,
                     justify="center").pack(pady=40)
            tk.Frame(self.list_frame, bg=styles.JINX_BG, height=1).pack(fill="x", pady=(0, 6))
            return
    
        # column headers
        header = tk.Frame(self.list_frame, bg=styles.JINX_BG)
        header.pack(fill="x", pady=(0, 8))
        for header_text, pad in [("#", 8), ("date", 24), ("hrs", 16), ("streak", 16), ("dist.", 16), ("score", 16)]:
            tk.Label(header, text=header_text, font=("Cinzel", 9),
                     fg=styles.JINX_BLUE, bg=styles.JINX_BG, padx=pad).pack(side="left")
    
        # divider
        tk.Frame(self.list_frame, bg=styles.JINX_DIVIDER, height=1).pack(fill="x", pady=(0, 6))
    
        # rows
        for i, s in enumerate(sessions[:10]):
            row = tk.Frame(self.list_frame, bg="#050d1a")
            row.pack(fill="x", pady=3)
            rank_color = styles.JINX_BLUE
            for rank_text, w in [
                (f"#{i+1}", 3),
                (s["date"], 10),
                (str(s["duration_hrs"]), 6),
                (str(s["longest_streak"]), 7),
                (str(s["distractions"]), 6),
                (str(s["score"]), 6),
            ]:
                tk.Label(row, text=rank_text, font=("Cinzel", 12),
                         fg=rank_color, bg=styles.JINX_BG).pack(side="left", expand=True)

    def _load(self):
        if not os.path.exists(SESSIONS_FILE):
            return []
        with open(SESSIONS_FILE, "r") as f:
            return json.load(f)
