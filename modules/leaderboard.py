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
        content = tk.Frame(self.canvas, bg="#0a1628") # blue tinted 
        self.canvas.create_window(190, 10, window=content, anchor="n")

        # header
        tk.Label(content, text="✦ Hall of Focus ✦",
                 font=("Cinzel", 18, "bold"), fg="#5ee7ff",  # Jinx electric blue
                 bg="#050d1a").pack(pady=(24, 4))

        tk.Label(content, text="BOOM! The Winner's Circle",
                 font=("Cinzel", 11, "italic"), fg="#7dd3fc",  # sky blue
                 bg="#050d1a").pack(pady=(0, 16))
        
        # sessions list
        self.list_frame = tk.Frame(content, bg=styles.BG_DARK)
        self.list_frame.pack(fill="both", expand=True, padx=20)
        
        self._render_sessions()

        # clear button
        tk.Label(self.window, text="clear history", font=styles.FONT_FOOTER,
                 fg="#4a7fa5", bg="#050d1a", cursor="hand2").pack(pady=12)

    def _render_sessions(self):
        # empty string bg = transparent in tkinter
        tk.Label(self.list_frame, text="Nothing to see here...yet.\nBack to the books, Cupcake!",
                     font=("Cinzel", 13, "italic"),
                     fg="#7dd3fc", bg="#050d1a", #blue
                     justify="center").pack(pady=40)
        header = tk.Frame(self.list_frame, bg="#050d1a")
        tk.Frame(self.list_frame, bg=styles.PURPLE_DIM, height=1).pack(fill="x", pady=(0, 6)) #keep colored
        row = tk.Frame(self.list_frame, bg="#050d1a")
        row.pack(fill="x", pady=3)
        
        tk.Label(row, text=text, font=("Cinzel", 12),
                 fg=rank_color, bg="#050d1a",
                 width=w, anchor="w").pack(side="left")
        
        sessions = self._load()

        if not sessions:
            tk.Label(self.list_frame, text="Nothing to see here... yet.\nBack to the books, Cupcake!",
                     font=("Cinzel", 13, "italic"),
                     fg=styles.GREY_MUTED, bg="#050d1a",
                     justify="center").pack(pady=40)
            return

        # column headers
        header = tk.Frame(self.list_frame, bg=styles.BG_DARK)
        header.pack(fill="x", pady=(0, 8))
        for header_text, w in [("#", 3), ("date", 10), ("mins", 6), ("streak", 7), ("dist.", 6), ("score", 6)]:
            tk.Label(header, text=header_text, font=("Cinzel", 9),
                     fg="#5ee7ff", bg="#050d1a", # electric blue
                     width=w, anchor="w").pack(side="left")

        # divider
        tk.Frame(self.list_frame, bg=#1e3a5f, height=1).pack(fill="x", pady=(0, 6))

        # rows
        for i, s in enumerate(sessions[:10]):  # top 10
            row = tk.Frame(self.list_frame, bg="#050d1a")
            row.pack(fill="x", pady=3)

            rank_color = "#5ee7ff" if i == 0 else "#7dd3fc" if i < 3 else "#4a7fa5"
            for rank_text, w in [
                (f"#{i+1}", 3),
                (s["date"], 10),
                (str(s["duration_mins"]), 6),
                (str(s["longest_streak"]), 7),
                (str(s["distractions"]), 6),
                (str(s["score"]), 6),
            ]:
                tk.Label(row, text=rank_text, font=("Cinzel", 12),
                         fg=rank_color, bg="#050d1a",
                         width=w, anchor="w").pack(side="left")

    def _load(self):
        if not os.path.exists(SESSIONS_FILE):
            return []
        with open(SESSIONS_FILE, "r") as f:
            return json.load(f)
