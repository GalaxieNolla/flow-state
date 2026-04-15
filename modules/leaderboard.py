import tkinter as tk
import json
import os
from datetime import datetime
from visuals import styles
from PIL import Image, ImageTk

SESSIONS_FILE = os.path.join(os.path.dirname(__file__), "sessions.json")
VISUALS_DIR = os.path.join(os.path.dirname(__file__), "..", "visuals", "images")


class Leaderboard:
    def __init__(self, root, session_tracker=None):
        self.root = root
        self.window = None
        self.session_tracker = session_tracker

    def open(self):
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return

        self.window = tk.Toplevel(self.root)
        self.window.title("Leaderboard")
        self.window.configure(bg=styles.BG_DARK)
        self.window.attributes("-topmost", True)

        # background
        bg_path = os.path.join(os.path.dirname(__file__), "..", "visuals", "leader background.png")
        bg_img = Image.open(bg_path).resize((1320, 600), Image.Resampling.LANCZOS)
        self.bg_image = ImageTk.PhotoImage(bg_img)
        W, H = bg_img.width, bg_img.height

        self.window.geometry(f"{W}x{H}")
        self.canvas = tk.Canvas(self.window, width=W, height=H, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")

        # load panel images
        left_path = os.path.join(VISUALS_DIR, "left-blue.png")
        right_path = os.path.join(VISUALS_DIR, "right-pink.png")

        left_img = Image.open(left_path).convert("RGBA")
        right_img = Image.open(right_path).convert("RGBA")

        # scale panels to fit side by side with padding
        panel_w = W // 2 - 40
        panel_h = H - 60

        left_img = left_img.resize((panel_w, panel_h), Image.Resampling.LANCZOS)
        right_img = right_img.resize((panel_w, panel_h), Image.Resampling.LANCZOS)

        self.left_panel_img = ImageTk.PhotoImage(left_img)
        self.right_panel_img = ImageTk.PhotoImage(right_img)

        # place panels
        left_x = W // 4
        right_x = W * 3 // 4
        panel_y = H // 2

        self.canvas.create_image(left_x, panel_y, image=self.left_panel_img, anchor="center")
        self.canvas.create_image(right_x, panel_y, image=self.right_panel_img, anchor="center")

        # winner's circle header
        self.canvas.create_text(left_x, 40,
            text="✦ Winner's Circle ✦",
            font=("Cinzel", 16, "bold"), fill=styles.JINX_BLUE)

        # current session header
        self.canvas.create_text(right_x, 40,
            text="✦ Current Session ✦",
            font=("Cinzel", 16, "bold"), fill="#f9a8d4")  # pink for right panel

        # left panel content — top sessions
        left_frame = tk.Frame(self.canvas, bg="")
        try:
            left_frame.config(bg="systemTransparent")
        except:
            left_frame.config(bg=styles.JINX_BG)
        self.canvas.create_window(left_x, 70, window=left_frame, anchor="n")
        self._render_winners(left_frame, panel_w - 40)

        # right panel content — current session
        right_frame = tk.Frame(self.canvas)
        try:
            right_frame.config(bg="systemTransparent")
        except:
            right_frame.config(bg="#1a0a1a")
        self.canvas.create_window(right_x, 70, window=right_frame, anchor="n")
        self._render_current_session(right_frame)

    def _render_winners(self, frame, width):
        sessions = self._load()

        # column headers
        header = tk.Frame(frame, bg=frame.cget("bg"))
        header.pack(fill="x", pady=(8, 4), padx=10)
        for text in ["#", "date", "hrs", "streak", "dist.", "score"]:
            tk.Label(header, text=text, font=("Cinzel", 9),
                     fg=styles.JINX_BLUE, bg=frame.cget("bg")).pack(side="left", expand=True)

        tk.Frame(frame, bg=styles.JINX_BLUE, height=1).pack(fill="x", padx=10, pady=(0, 6))

        if not sessions:
            tk.Label(frame, text="nothing here yet...\ngo make some chaos 💙",
                     font=("Cinzel", 11, "italic"),
                     fg=styles.JINX_BLUE_MID, bg=frame.cget("bg"),
                     justify="center").pack(pady=20)
            return

        for i, s in enumerate(sessions[:5]):
            row = tk.Frame(frame, bg=frame.cget("bg"))
            row.pack(fill="x", pady=2, padx=10)
            color = styles.JINX_BLUE if i == 0 else styles.JINX_BLUE_MID if i < 3 else styles.JINX_BLUE_DARK
            for text in [
                f"#{i+1}",
                s["date"],
                str(s.get("duration_hrs", round(s.get("duration_mins", 0) / 60, 1))),
                str(s["longest_streak"]),
                str(s["distractions"]),
                str(s["score"]),
            ]:
                tk.Label(row, text=text, font=("Cinzel", 10),
                         fg=color, bg=frame.cget("bg")).pack(side="left", expand=True)

    def _render_current_session(self, frame):
        if not self.session_tracker:
            tk.Label(frame, text="no active session",
                     font=("Cinzel", 11, "italic"),
                     fg="#f9a8d4", bg=frame.cget("bg")).pack(pady=20)
            return

        duration_hrs = round((
            __import__('time').time() - self.session_tracker.session_start) / 3600, 1)
        streak_hrs = round((
            __import__('time').time() - self.session_tracker.nudge.streak_start) / 3600, 1)
        distractions = self.session_tracker.distractions
        score = self.session_tracker._calculate_score(
            int(duration_hrs * 60), int(streak_hrs * 60), distractions)

        pink = "#f9a8d4"
        bg = frame.cget("bg")

        tk.Frame(frame, bg=pink, height=1).pack(fill="x", padx=10, pady=(8, 10))

        for label, value in [
            ("session time", f"{duration_hrs} hrs"),
            ("focus streak", f"{streak_hrs} hrs"),
            ("distractions", str(distractions)),
            ("score", str(score)),
        ]:
            row = tk.Frame(frame, bg=bg)
            row.pack(fill="x", pady=4, padx=20)
            tk.Label(row, text=label, font=("Cinzel", 9),
                     fg=pink, bg=bg, anchor="w").pack(side="left", expand=True)
            tk.Label(row, text=value, font=("Cinzel", 12, "bold"),
                     fg="white", bg=bg, anchor="e").pack(side="right")

        # refresh button
        tk.Label(frame, text="↻ refresh", font=styles.FONT_FOOTER,
                 fg=pink, bg=bg, cursor="hand2").pack(pady=(12, 0))

    def _load(self):
        if not os.path.exists(SESSIONS_FILE):
            return []
        with open(SESSIONS_FILE, "r") as f:
            return json.load(f)
