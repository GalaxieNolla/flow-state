import tkinter as tk
import json
import os
import time
from visuals import styles
from PIL import Image, ImageTk

SESSIONS_FILE = os.path.join(os.path.dirname(__file__), "sessions.json")
VISUALS_DIR   = os.path.join(os.path.dirname(__file__), "..", "visuals", "images")

W, H = 1100, 600


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
        self.window.geometry(f"{W}x{H}")
        self.window.resizable(False, False)
        self.window.attributes("-topmost", True)
        self.window.configure(bg=PANEL_BG)

        # ── Background ────────────────────────────────────────────────────────
        bg_path = os.path.join(os.path.dirname(__file__), "..", "visuals", "leader background.png")
        bg_img = Image.open(bg_path).resize((W, H), Image.Resampling.LANCZOS)
        self.bg_image = ImageTk.PhotoImage(bg_img)

        self.canvas = tk.Canvas(self.window, width=W, height=H,
                                highlightthickness=0, bg=PANEL_BG)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")

        # ── Layout constants ──────────────────────────────────────────────────
        pad       = 24
        left_w    = 680
        right_w   = 340
        left_x    = pad
        right_x   = left_x + left_w + pad
        top_y     = pad
        panel_h   = H - pad * 2

        # ── Draw panels ───────────────────────────────────────────────────────
        self._draw_panel(left_x,  top_y, left_w,  panel_h)
        self._draw_panel(right_x, top_y, right_w, panel_h)

        # ── Winners panel content ─────────────────────────────────────────────
        lc = left_x + left_w // 2
        self.canvas.create_text(lc, top_y + 30,
            text="✦  Winner's Circle  ✦",
            font=("Cinzel", 20, "bold"), fill=styles.GOLD)
        self.canvas.create_line(
            left_x + 40, top_y + 52,
            left_x + left_w - 40, top_y + 52,
            fill=styles.AMBER_DIM, width=1)
        self._draw_winners(left_x, top_y + 65, left_w)

        # ── Current session panel content ─────────────────────────────────────
        rc = right_x + right_w // 2
        self.canvas.create_text(rc, top_y + 30,
            text="✦  Current Session  ✦",
            font=("Cinzel", 14, "bold"), fill=styles.GOLD)
        self.canvas.create_line(
            right_x + 24, top_y + 52,
            right_x + right_w - 24, top_y + 52,
            fill=styles.AMBER_DIM, width=1)

        self._rc = rc
        self._right_x = right_x
        self._right_w = right_w
        self._top_y = top_y
        self._draw_current_session(rc, top_y + 70)
        self._start_session_ticker()

    def _draw_panel(self, x, y, w, h):
        """
        Draw a dark rounded-rectangle panel with amber border.
        """
        r = 18
        # filled rounded rect via polygon approximation
        self.canvas.create_rectangle(
            x + r, y, x + w - r, y + h,
            fill=styles.PANEL_BG, outline="", stipple=""
        )
        self.canvas.create_rectangle(
            x, y + r, x + w, y + h - r,
            fill=styles.PANEL_BG, outline=""
        )
        # corners
        for cx2, cy2, start in [
            (x + r,     y + r,     180),
            (x + w - r, y + r,      90),
            (x + w - r, y + h - r,   0),
            (x + r,     y + h - r, 270),
        ]
