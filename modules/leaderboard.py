import tkinter as tk
import json
import os
import time
from visuals import styles
from PIL import Image, ImageTk

SESSIONS_FILE = os.path.join(os.path.dirname(__file__), "sessions.json")
VISUALS_DIR   = os.path.join(os.path.dirname(__file__), "..", "visuals", "images")

# ── Palette ───────────────────────────────────────────────────────────────────
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
        self.window.attributes("-topmost", True)
        self.window.configure(bg=styles.PANEL_BG)

        # ── Background ────────────────────────────────────────────────────────
        bg_path = os.path.join(os.path.dirname(__file__), "..", "visuals", "leaderboard.webp")
        bg_img = Image.open(bg_path).resize((W, H), Image.Resampling.LANCZOS)
        self.bg_image = ImageTk.PhotoImage(bg_img)

        self.canvas = tk.Canvas(self.window, width=W, height=H,
                                highlightthickness=0, bg=styles.PANEL_BG)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")

        # Layout vars
        pad = 24
        left_w = 300 # adjust for left leaderboard panel
        right_w = 280
        left_x = pad
        right_x = W * 0.7 #adjust for LHS of right panel
        top_y = H * 0.1
        right_y = H * 0.15
        panel_h = H * 0.75 # height of panel
        right_h = 380 #right panel, curr session

        # ── Draw panels ───────────────────────────────────────────────────────
        self._draw_panel(left_x,  top_y, left_w,  panel_h)
        self._draw_panel(right_x, right_y, right_w, right_h)

        # ── Winners panel content ─────────────────────────────────────────────
        lc = left_x + left_w // 2
        self.canvas.create_text(lc, top_y + 30,
            text="✦  Winner's Circle  ✦",
            font=("Cinzel", 20, "bold"), fill=styles.AMBER_DIM)
        self.canvas.create_line(
            left_x + 40, top_y + 52,
            left_x + left_w - 40, top_y + 52,
            fill=styles.AMBER_DIM, width=1)
        self._draw_winners(left_x, top_y + 65, left_w)

        # ── Current session panel content ─────────────────────────────────────
        rc = right_x + right_w // 2
        self.canvas.create_text(rc, right_y + 30,
            text="✦  Current Session  ✦",
            font=("Cinzel", 14, "bold"), fill=styles.AMBER_DIM)
        self.canvas.create_line(
            right_x + 24, right_y + 52,
            right_x + right_w - 24, right_y + 52,
            fill=styles.AMBER_DIM, width=1)

        self._rc = rc
        right_x = W - right_w - pad #DEBUG sizing for right panel
        self._right_w = right_w
        self._right_y = right_y
        self._draw_current_session(rc, right_y + 70)
        self._start_session_ticker()
        self.window.bind("<Configure>", self._on_resize) #to help resize

    def _draw_panel(self, x, y, w, h):
        # create borders, so can still see background
        self.canvas.create_rectangle(
            x, y, x + w, y + h,
            fill="", outline=styles.AMBER_DIM, width=1
        )

    def _draw_winners(self, panel_x, start_y, panel_w, h=600):
        sessions = self._load()

        # column x positions
        col_x = {
            "rank":   panel_x + 25,
            "date":   panel_x + 90,
            "hrs":    panel_x + 150,
            "streak": panel_x + 190,
            "dist":   panel_x + 230,
            "score":  panel_x + 270,
        }

        # header row
        for key, label in [("rank","#"), ("date","Date"), ("hrs","Hrs"),
                            ("streak","Streak"), ("dist","Dist"), ("score","Score")]:
            self.canvas.create_text(
                col_x[key], start_y,
                text=label.upper(),
                font=("Cinzel", 10, "bold"),
                fill=styles.AMBER_DIM, anchor="center"
            )
        self.canvas.create_line(
            panel_x + 20, start_y + 16,
            panel_x + panel_w - 20, start_y + 16,
            fill=styles.DIVIDER, width=1
        )

        if not sessions:
            self.canvas.create_text(
                panel_x + panel_w // 2, start_y + 100,
                text="nothing here yet...\ngo paint the town blue, cupcake",
                font=("Cinzel", 16, "italic"),
                fill=styles.TEXT_DIM, justify="center"
            )
            return

        row_h = int(h * 0.063)  # ~38px
        fs = max(9, int(13 * h / 600))
        
        row_h = 38
        for i, s in enumerate(sessions[:10]):
            y = start_y + 28 + i * row_h

            # alternating row bg
            if i % 2 == 0:
                self.canvas.create_rectangle(
                    panel_x + 12, y - 12,
                    panel_x + panel_w - 12, y + row_h - 14,
                    fill=styles.ROW_ALT, outline=""
                )

            # rank badge
            rank_colors = {0: (styles.GOLD, "#3d2800"), 1: (styles.SILVER, "#2a2a2a"), 2: (styles.BRONZE, "#2a1500")}
            badge_fill, badge_text = rank_colors.get(i, (styles.PANEL_BG, styles.TEXT_DIM))
            r = 13
            bx = col_x["rank"]
            self.canvas.create_oval(
                bx - r, y - r, bx + r, y + r,
                fill=badge_fill, outline=""
            )
            self.canvas.create_text(
                bx, y,
                text=str(i + 1),
                font=("Cinzel", fs, "bold"),
                fill=badge_text if i < 3 else styles.TEXT_DIM
            )

            # row text color
            color = styles.TEXT_BRIGHT if i == 0 else styles.TEXT_MID if i < 3 else styles.TEXT_DIM

            dur = s.get("duration_hrs", round(s.get("duration_mins", 0) / 60, 1))
            values = {
                "date":   s["date"],
                "hrs":    str(dur),
                "streak": str(s["longest_streak"]),
                "dist":   str(s["distractions"]),
                "score":  str(s["score"]),
            }
            for key, val in values.items():
                self.canvas.create_text(
                    col_x[key], y,
                    text=val,
                    font=("Cinzel", fs),
                    fill=styles.AMBER_DIM if key == "score" and i < 3 else color,
                    anchor="center"
                )

    def _draw_current_session(self, cx, start_y):
        if not self.session_tracker:
            self.canvas.create_text(cx, start_y + 60,
                text="no active session",
                font=("Cinzel", 13, "italic"),
                fill=styles.AMBER_MID, tags="session_item")
            return

        elapsed       = time.time() - self.session_tracker.session_start
        streak_elapsed = time.time() - self.session_tracker.nudge.streak_start
        distractions  = self.session_tracker.distractions

        def fmt(secs):
            h = int(secs // 3600)
            m = int((secs % 3600) // 60)
            s = int(secs % 60)
            return f"{h}:{m:02d}:{s:02d}"

        score = self.session_tracker._calculate_score(
            elapsed / 3600, int(streak_elapsed // 60), distractions)

        rows = [
            ("Session Time",  fmt(elapsed)),
            ("Focus Streak",  fmt(streak_elapsed)),
            ("Distractions",  str(distractions)),
            ("Score",         str(score)),
        ]

        for i, (label, value) in enumerate(rows):
            y = start_y + i * 65 #for row spacing
            # label
            self.canvas.create_text(cx, y,
                text=label.upper(),
                font=("Cinzel", 10, "bold"),
                fill=styles.AMBER_DIM, tags="session_item")
            # divider under label
            self.canvas.create_line(
                cx - 80, y + 14, cx + 80, y + 14,
                fill=styles.DIVIDER, width=1, tags="session_item")
            # value
            self.canvas.create_text(cx, y + 34,
                text=value,
                font=("Cinzel", 22, "bold"),
                fill=styles.AMBER_DIM if label == "Score" else styles.TEXT_BRIGHT,
                tags="session_item")

        # refresh button
        refresh_y = start_y + len(rows) * 65 + 10
        ref = self.canvas.create_text(cx, refresh_y,
            text="↻  refresh",
            font=("Cinzel", 11),
            fill=styles.AMBER_DIM, tags="session_item")
        self.canvas.tag_bind(ref, "<Button-1>", lambda e: self._refresh())
        self.canvas.tag_bind(ref, "<Enter>",
            lambda e: self.canvas.itemconfig(ref, fill=styles.GOLD))
        self.canvas.tag_bind(ref, "<Leave>",
            lambda e: self.canvas.itemconfig(ref, fill=styles.AMBER_DIM))

    def _refresh(self):
        if self.window and self.window.winfo_exists():
            for item in self.canvas.find_withtag("session_item"):
                self.canvas.delete(item)
            h = getattr(self, '_h', 600)
            self._draw_current_session(self._rc, self._right_y + int(h * 0.117))

    def _start_session_ticker(self):
        if self.window and self.window.winfo_exists():
            for item in self.canvas.find_withtag("session_item"):
                self.canvas.delete(item)
            h = getattr(self, '_h', 600)
            self._draw_current_session(self._rc, self._right_y + int(h * 0.117))
            self.root.after(1000, self._start_session_ticker)

    def _load(self):
        if not os.path.exists(SESSIONS_FILE):
            return []
        with open(SESSIONS_FILE, "r") as f:
            return json.load(f)

    # Resize ---------------------------------------------------------
    def _on_resize(self, event):
        if event.widget != self.window:
            return
        if hasattr(self, '_resize_id') and self._resize_id:
            self.window.after_cancel(self._resize_id)
        self._resize_id = self.window.after(80, self._redraw)

    def _redraw(self):
        self.canvas.delete("all")
        w = self.window.winfo_width()
        h = self.window.winfo_height()
    
        # redraw background
        bg_path = os.path.join(os.path.dirname(__file__), "..", "visuals", "leaderboard.webp")
        bg_img = Image.open(bg_path).resize((w, h), Image.Resampling.LANCZOS)
        self.bg_image = ImageTk.PhotoImage(bg_img)
        self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")
    
        # layout — all relative to current w, h
        pad     = int(w * 0.022)
        left_w  = int(w * 0.27)   # ~300px at 1100
        right_w = int(w * 0.255)  # ~280px at 1100
        left_x  = pad
        right_x = int(w * 0.7)
        top_y   = int(h * 0.1)
        right_y = int(h * 0.15)
        panel_h = int(h * 0.75)
        right_h = int(h * 0.633)  # ~380px at 600
    
        self._draw_panel(left_x,  top_y,   left_w,  panel_h)
        self._draw_panel(right_x, right_y, right_w, right_h)
    
        # winners title + content
        lc = left_x + left_w // 2
        fs = max(12, int(20 * h / 600))
        self.canvas.create_text(lc, top_y + int(h * 0.05),
            text="✦  Winner's Circle  ✦",
            font=("Cinzel", fs, "bold"), fill=styles.AMBER_DIM)
        self.canvas.create_line(
            left_x + 40, top_y + int(h * 0.087),
            left_x + left_w - 40, top_y + int(h * 0.087),
            fill=styles.AMBER_DIM, width=1)
        self._draw_winners(left_x, top_y + int(h * 0.108), left_w, h)
    
        # current session title + content
        rc = right_x + right_w // 2
        fs2 = max(10, int(14 * h / 600))
        self.canvas.create_text(rc, right_y + int(h * 0.05),
            text="✦  Current Session  ✦",
            font=("Cinzel", fs2, "bold"), fill=styles.AMBER_DIM)
        self.canvas.create_line(
            right_x + 24, right_y + int(h * 0.087),
            right_x + right_w - 24, right_y + int(h * 0.087),
            fill=styles.AMBER_DIM, width=1)
    
        self._rc = rc
        self._right_w = right_w
        self._right_y = right_y
        self._h = h
        self._draw_current_session(rc, right_y + int(h * 0.117))
