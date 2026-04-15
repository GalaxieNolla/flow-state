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
        self.window.geometry("380x500")
        self.window.configure(bg=styles.BG_DARK)
        self.window.attributes("-topmost", True)

        # background image
        img_path = os.path.join(os.path.dirname(__file__), "..", "visuals", "leader background.png")
        self.bg_image = ImageTk.PhotoImage(Image.open(img_path).resize((380, 500)))
        self.canvas = tk.Canvas(self.window, width=380, height=500, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")

        # place all content on canvas
        content = tk.Frame(self.canvas, bg=styles.BG_DARK)  
        self.canvas.create_window(190, 10, window=content, anchor="n")

        # header
        tk.Label(content, text="✦ Hall of Focus ✦",
                 font=("Cinzel", 18, "bold"), fg=styles.GOLD_ACCENT,
                 bg=styles.BG_DARK).pack(pady=(24, 4))
        tk.Label(content, text="BOOM! The Winner's Circle",
                 font=("Cormorant Garamond", 11, "italic"), fg=styles.GREY_MUTED,
                 bg=styles.BG_DARK).pack(pady=(0, 16))
        
        # sessions list
        self.list_frame = tk.Frame(content, bg=styles.BG_DARK)
        self.list_frame.pack(fill="both", expand=True, padx=20)
        
        self._render_sessions()

        # clear button
        tk.Label(self.window, text="clear history", font=styles.FONT_FOOTER,
                 fg=styles.GREY_MUTED, bg=styles.BG_DARK, cursor="hand2").pack(pady=12)

    def _render_sessions(self):
        # empty string bg = transparent in tkinter
        tk.Label(self.list_frame, text="Nothing to see here... yet.\nBack to the books, Cupcake!",
                     font=("Cormorant Garamond", 13, "italic"),
                     fg=styles.GREY_MUTED, bg=styles.BG_DARK,
                     justify="center").pack(pady=40)
        header = tk.Frame(self.list_frame, bg=styles.BG_DARK)
        tk.Frame(self.list_frame, bg=styles.PURPLE_DIM, height=1).pack(fill="x", pady=(0, 6)) #keep colored
        row = tk.Frame(self.list_frame, bg=styles.BG_DARK)
        row.pack(fill="x", pady=3)
        
        tk.Label(row, text=text, font=("Cormorant Garamond", 12),
                 fg=rank_color, bg=styles.BG_DARK,
                 width=w, anchor="w").pack(side="left")
        
        sessions = self._load()

        if not sessions:
            tk.Label(self.list_frame, text="Nothing to see here... yet.\nBack to the books, Cupcake!",
                     font=("Cormorant Garamond", 13, "italic"),
                     fg=styles.GREY_MUTED, bg=styles.BG_DARK,
                     justify="center").pack(pady=40)
            return

        # column headers
        header = tk.Frame(self.list_frame, bg=styles.BG_DARK)
        header.pack(fill="x", pady=(0, 8))
        for text, w in [("#", 3), ("date", 10), ("mins", 6), ("streak", 7), ("dist.", 6), ("score", 6)]:
            tk.Label(header, text=text, font=("Cinzel", 9),
                     fg=styles.GOLD_ACCENT, bg=styles.BG_DARK,
                     width=w, anchor="w").pack(side="left")

        # divider
        tk.Frame(self.list_frame, bg=styles.PURPLE_DIM, height=1).pack(fill="x", pady=(0, 6))

        # rows
        for i, s in enumerate(sessions[:10]):  # top 10
            row = tk.Frame(self.list_frame, bg=styles.BG_DARK)
            row.pack(fill="x", pady=3)

            rank_color = styles.GOLD_ACCENT if i == 0 else styles.PURPLE_GLOW if i < 3 else styles.GREY_MUTED
            for text, w in [
                (f"#{i+1}", 3),
                (s["date"], 10),
                (str(s["duration_mins"]), 6),
                (str(s["longest_streak"]), 7),
                (str(s["distractions"]), 6),
                (str(s["score"]), 6),
            ]:
                tk.Label(row, text=text, font=("Cormorant Garamond", 12),
                         fg=rank_color, bg=styles.BG_DARK,
                         width=w, anchor="w").pack(side="left")

    def _load(self):
        if not os.path.exists(SESSIONS_FILE):
            return []
        with open(SESSIONS_FILE, "r") as f:
            return json.load(f)
