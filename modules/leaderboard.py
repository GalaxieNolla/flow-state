import tkinter as tk
import json
import os
import time
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
        bg_img = Image.open(bg_path).resize((1100, 580), Image.Resampling.LANCZOS)
        self.bg_image = ImageTk.PhotoImage(bg_img)
        W, H = bg_img.width, bg_img.height

        self.window.geometry(f"{W}x{H}")
        self.canvas = tk.Canvas(self.window, width=W, height=H, highlightthickness=0, bg=styles.BG_DARK)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")

        # panel dimensions
        panel_w_left = 800
        panel_w_right = 500
        panel_h_left = 540
        panel_h_right = 400
        left_x = -100
        right_x = 600
        panel_y_left = 30
        panel_y_right = 180

        # load + place left panel
        left_img = Image.open(os.path.join(VISUALS_DIR, "left-blue.png")).convert("RGBA")
        left_img = left_img.resize((panel_w_left, panel_h_left), Image.Resampling.LANCZOS)
        self.left_panel_img = ImageTk.PhotoImage(left_img)
        self.canvas.create_image(left_x, panel_y_left, image=self.left_panel_img, anchor="nw")

        # load + place right panel
        right_img = Image.open(os.path.join(VISUALS_DIR, "right-pink.png")).convert("RGBA")
        right_img = right_img.resize((panel_w_right, panel_h_right), Image.Resampling.LANCZOS)
        self.right_panel_img = ImageTk.PhotoImage(right_img)
        self.canvas.create_image(right_x, panel_y_right, image=self.right_panel_img, anchor="nw")

        # center x of each panel
        lc = left_x + panel_w_left // 2
        rc = right_x + panel_w_right // 2

        # headers
        self.canvas.create_text(lc, panel_y_left + 40, text="✦ Winner's Circle ✦",
            font=("Cinzel", 25, "bold"), fill="white")
        self.canvas.create_text(rc, panel_y_right + 50, text="✦ Current Session ✦",
            font=("Cinzel", 22, "bold"), fill="white")

        # dividers
        self.canvas.create_line(left_x + 190, panel_y_left + 70, left_x + panel_w_left - 190, panel_y_left + 70,
            fill=styles.JINX_BLUE, width=2)
        self.canvas.create_line(right_x + 90, panel_y_right + 75, right_x + panel_w_right - 90, panel_y_right + 75,
            fill="#ff69b4", width=2)

        self._draw_winners(lc, panel_y_left + 85, panel_w_left)
        self._draw_current_session(rc, panel_y_right + 65)

    def _draw_winners(self, cx, start_y, panel_w_left):
        sessions = self._load()
        col_spacing = 68
        cols = ["#", "date", "hrs", "streak", "dist", "score"]
        col_x = [cx - 160, cx - 90, cx - 20, cx + 45, cx + 105, cx + 160]

        # column headers
        for i, col in enumerate(cols):
            self.canvas.create_text(col_x[i], start_y,
                text=col, font=("Cinzel", 14), fill=styles.JINX_BLUE)

        self.canvas.create_line(cx - 180, start_y + 20, cx + 180, start_y + 20,
            fill=styles.JINX_DIVIDER, width=1)

        if not sessions:
            self.canvas.create_text(cx, start_y + 80,
                text="nothing here yet...\ngo make some chaos cupcake",
                font=("Cinzel", 20, "italic"), fill=styles.JINX_BLUE_MID,
                justify="center")
            return

        for i, s in enumerate(sessions[:5]):
            y = start_y + 50 + i * 34
            color = styles.JINX_BLUE if i == 0 else styles.JINX_BLUE_MID if i < 3 else styles.JINX_BLUE_DARK
            values = [
                f"#{i+1}",
                s["date"],
                str(s.get("duration_hrs", round(s.get("duration_mins", 0) / 60, 1))),
                str(s["longest_streak"]),
                str(s["distractions"]),
                str(s["score"]),
            ]
            for j, val in enumerate(values):
                self.canvas.create_text(col_x[j], y,
                    text=val, font=("Cinzel", 18), fill=color)

    def _draw_current_session(self, cx, start_y):
        pink = "#ff69b4"

        if not self.session_tracker:
            self.canvas.create_text(cx, start_y + 60,
                text="no active session", font=("Cinzel", 13, "italic"), fill=pink)
            return

        duration_hrs = round((time.time() - self.session_tracker.session_start) / 3600, 1)
        streak_hrs = round((time.time() - self.session_tracker.nudge.streak_start) / 3600, 1)
        distractions = self.session_tracker.distractions
        score = self.session_tracker._calculate_score(
            int(duration_hrs * 60), int(streak_hrs * 60), distractions)

        rows = [
            ("session time", f"{duration_hrs} hrs"),
            ("focus streak", f"{streak_hrs} hrs"),
            ("distractions", str(distractions)),
            ("score",        str(score)),
        ]

        for i, (label, value) in enumerate(rows):
            y = start_y + 30 + i * 60
            self.canvas.create_text(cx, y,
                text=label, font=("Cinzel", 18, "bold"), fill=pink)
            self.canvas.create_text(cx, y + 26,
                text=value, font=("Cinzel", 22, "bold"), fill="white")

        # refresh — clickable text
        refresh_y = start_y + 280
        refresh = self.canvas.create_text(cx, refresh_y,
            text="↻ refresh", font=("Cinzel", 12), fill=pink)
        self.canvas.tag_bind(refresh, "<Button-1>", lambda e: self._refresh())

    def _refresh(self):
        if self.window and self.window.winfo_exists():
            self.window.destroy()
            self.window = None
            self.open()

    def _load(self):
        if not os.path.exists(SESSIONS_FILE):
            return []
        with open(SESSIONS_FILE, "r") as f:
            return json.load(f)
