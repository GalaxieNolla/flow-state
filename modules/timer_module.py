import tkinter as tk
from visuals import styles
from PIL import Image, ImageTk


class StudyTimer:
    def __init__(self, root, canvas, app):
        self.root = root
        self.canvas = canvas
        self.app = app
        self._resize_id = None

        # Timer state
        self.seconds_left = 0
        self.total_seconds = 0
        self.is_break = False
        self.is_running = False
        self.is_paused = False
        self.after_id = None
        self.center_image = None

        # Pomodoro config
        self.study_minutes = 25
        self.short_break_mins = 5
        self.long_break_mins = 15
        self.rounds_goal = 4
        self.current_round = 0

        self.ui_widgets = []

        # ── Persistent canvas text items ──────────────────────────────────────
        self.clock_display = self.canvas.create_text(
            256, 310, text="",
            font=("Courier New", 52, "bold"),
            fill=styles.PURPLE_GLOW,
            state="hidden"
        )
        self.session_label_id = self.canvas.create_text(
            256, 255, text="",
            font=("Cinzel", 11, "bold"),
            fill="#a78bfa",
            state="hidden"
        )
        self.round_label_id = self.canvas.create_text(
            256, 370, text="",
            font=("Cinzel", 11),
            fill="#6b4c8a",
            state="hidden"
        )

    # ── Widget helpers ────────────────────────────────────────────────────────
    def _wh(self):
        """
        Return current canvas w & h.
        """
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        return w, h

    def _place(self, widget, x, y):
        win_id = self.canvas.create_window(x, y, window=widget)
        self.ui_widgets.append((widget, win_id))
        return win_id

    def _clear_ui(self):
        for widget, win_id in self.ui_widgets:
            try:
                self.canvas.delete(win_id)
                widget.destroy()
            except Exception:
                pass
        self.ui_widgets.clear()
        self.canvas.delete("timer_elements")
        self.canvas.delete("timer_bg")
        self.canvas.delete("timer_ring")
        self.canvas.delete("progress_bar")

    def _hide_clock(self):
        self.canvas.itemconfig(self.clock_display, state="hidden")
        self.canvas.itemconfig(self.session_label_id, state="hidden")
        self.canvas.itemconfig(self.round_label_id, state="hidden")

    def _show_clock(self):
        self.canvas.itemconfig(self.clock_display, state="normal")
        self.canvas.itemconfig(self.session_label_id, state="normal")
        self.canvas.itemconfig(self.round_label_id, state="normal")

    def stop(self):
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self.is_running = False
        self.is_paused = False
        self._clear_ui()
        self._hide_clock()
        self.root.unbind("<Configure>") #prev stagnant binding

    # ── Progress Bar ──────────────────────────────────────────────────────────

    def _draw_progress_bar(self):
        """
        Responsive progress bar over all N rounds. Incrementally increases per round.
        """
        self.canvas.delete("progress_bar")
        if self.is_break:
            return

        w = self.canvas.winfo_width() or 512
        bar_h = 6        # bar height
        tick_h = 12      # tick mark height (extends above+below bar)
        y = 18           # top of bar
        color = styles.PURPLE_GLOW
        bg_color = "#1e0f33"

        # Background track
        self.canvas.create_rectangle(
            0, y, w, y + bar_h,
            fill=bg_color, outline="",
            tags="progress_bar"
        )

        # Completed rounds — fully filled segments
        seg_w = w / self.rounds_goal
        for r in range(self.current_round):
            x0 = r * seg_w
            x1 = (r + 1) * seg_w
            self.canvas.create_rectangle(
                x0, y, x1, y + bar_h,
                fill=color, outline="",
                tags="progress_bar"
            )

        # Current round — fills based on elapsed time
        if not self.is_break and self.total_seconds > 0:
            elapsed_frac = 1.0 - (self.seconds_left / self.total_seconds)
            x0 = self.current_round * seg_w
            x1 = x0 + seg_w * elapsed_frac
            self.canvas.create_rectangle(
                x0, y, x1, y + bar_h,
                fill=color, outline="",
                tags="progress_bar"
            )

        # Tick marks
        for r in range(1, self.rounds_goal):
            x = r * seg_w
            self.canvas.create_line(
                x, y - (tick_h - bar_h) // 2,
                x, y + bar_h + (tick_h - bar_h) // 2,
                fill="#3d2b56", width=2,
                tags="progress_bar"
            )

        # Raise clock items above bar
        self.canvas.tag_raise(self.session_label_id)
        self.canvas.tag_raise(self.clock_display)
        self.canvas.tag_raise(self.round_label_id)

    # ── Setup Screen ──────────────────────────────────────────────────────────

    def show_setup(self):
        self._clear_ui()
        self._hide_clock()
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self.is_running = False
        self.is_paused = False
        self.current_round = 0

        self.root.update_idletasks()
        self.root.after(10, self._draw_setup)
        self.root.bind("<Configure>", self._on_setup_resize) #resizing semantics

    def _draw_setup(self):
        self._clear_ui()
        self._draw_nav_bar()
        self._draw_setup_controls()

    def _on_setup_resize(self, event):
        if event.widget != self.root:
            return
        if self._resize_id:
            self.root.after_cancel(self._resize_id)
        self._resize_id = self.root.after(80, self._redraw_setup)

    def _redraw_setup(self):
        self._resize_id = None
        self._clear_ui()
        self._draw_nav_bar()
        self._draw_setup_controls()
    
    def _draw_nav_bar(self):
        w, h = self._wh()
        cx = w // 2
        s = self._scale()
    
        menu_btn = tk.Label(
            self.canvas, text="← Menu",
            font=("Cinzel", max(8, int(11 * s)), "bold"),
            fg="#6b4c8a", bg="#0a0514",
            cursor="hand2", padx=8, pady=4
        )
        menu_btn.bind("<Enter>", lambda e: menu_btn.config(fg=styles.PURPLE_GLOW))
        menu_btn.bind("<Leave>", lambda e: menu_btn.config(fg="#6b4c8a"))
        menu_btn.bind("<Button-1>", lambda e: self.app.return_to_menu())
        self._place(menu_btn, x=int(w * 0.08), y=int(h * 0.11))
    
        lb_btn = tk.Label(
            self.canvas, text="Leaderboard →",
            font=("Cinzel", max(8, int(11 * s)), "bold"),
            fg="#6b4c8a", bg="#0a0514",
            cursor="hand2", padx=8, pady=4
        )
        lb_btn.bind("<Enter>", lambda e: lb_btn.config(fg=styles.PURPLE_GLOW))
        lb_btn.bind("<Leave>", lambda e: lb_btn.config(fg="#6b4c8a"))
        lb_btn.bind("<Button-1>", lambda e: self.app.leaderboard.open())
        self._place(lb_btn, x=int(w * 0.88), y=int(h * 0.11))

    def _draw_setup_controls(self):
        w, h = self._wh()
        cx = w // 2
        s = self._scale()
    
        title = tk.Label(
            self.canvas, text="POMODORO",
            font=("Cinzel", max(12, int(22 * s)), "bold"),
            fg=styles.PURPLE_GLOW, bg="#0a0514"
        )
        self._place(title, x=cx, y=int(h * 0.25))
    
        time_label = tk.Label(
            self.canvas, text="STUDY TIME",
            font=("Cinzel", max(7, int(9 * s)), "bold"),
            fg="#6b4c8a", bg="#0a0514"
        )
        self._place(time_label, x=cx, y=int(h * 0.32))
    
        preset_frame = tk.Frame(self.canvas, bg="#0a0514")
        presets = [15, 25, 45, 60]
        self._preset_btns = {}
        for mins in presets:
            is_sel = mins == self.study_minutes
            btn = tk.Label(
                preset_frame, text=f"{mins}",
                font=("Cinzel", max(8, int(14 * s)), "bold"),
                fg="#120921" if is_sel else "#4a3a6a",
                bg=styles.PURPLE_GLOW if is_sel else "#1a0f2e",
                width=3, pady=5, cursor="hand2"
            )
            btn.pack(side="left", padx=5)
            self._preset_btns[mins] = btn
        for mins, btn in self._preset_btns.items():
            btn.bind("<Button-1>", lambda e, m=mins: self._select_time(m))
        self._place(preset_frame, x=cx, y=int(h * 0.4))
    
        rounds_label = tk.Label(
            self.canvas, text="ROUNDS",
            font=("Cinzel", max(7, int(9 * s)), "bold"),
            fg="#6b4c8a", bg="#0a0514"
        )
        self._place(rounds_label, x=cx, y=int(h * 0.47))
    
        rounds_frame = tk.Frame(self.canvas, bg="#0a0514")
        minus_btn = tk.Label(
            rounds_frame, text="−",
            font=("Cinzel", max(12, int(16 * s)), "bold"),
            fg="#a78bfa", bg="#0a0514",
            cursor="hand2", padx=10
        )
        minus_btn.pack(side="left")
        minus_btn.bind("<Button-1>", lambda e: self._change_rounds(-1))
        self.rounds_display = tk.Label(
            rounds_frame, text=str(self.rounds_goal),
            font=("Cinzel", max(10, int(13 * s)), "bold"),
            fg=styles.PURPLE_GLOW, bg="#0a0514", width=2
        )
        self.rounds_display.pack(side="left")
        plus_btn = tk.Label(
            rounds_frame, text="+",
            font=("Cinzel", max(12, int(16 * s)), "bold"),
            fg="#a78bfa", bg="#0a0514",
            cursor="hand2", padx=10
        )
        plus_btn.pack(side="left")
        plus_btn.bind("<Button-1>", lambda e: self._change_rounds(1))
        self._place(rounds_frame, x=cx, y=int(h * 0.53))
    
        self._break_info = tk.Label(
            self.canvas,
            text=f"Breaks: 5 min per round (short)  ·  15 min after {self.rounds_goal} rounds (long)",
            font=("Georgia", max(10, int(13 * s)), "bold italic"),
            fg="#3d2b56", bg="#0a0514"
        )
        self._place(self._break_info, x=cx, y=int(h * 0.58))
    
        start_btn = tk.Label(
            self.canvas, text="▶   START",
            font=("Cinzel", max(13, int(18 * s)), "bold"),
            fg="#120921", bg=styles.PURPLE_GLOW,
            padx=22, pady=8, cursor="hand2"
        )
        start_btn.bind("<Button-1>", lambda e: self._start_session())
        start_btn.bind("<Enter>", lambda e: start_btn.config(bg="#b06eff"))
        start_btn.bind("<Leave>", lambda e: start_btn.config(bg=styles.PURPLE_GLOW))
        self._place(start_btn, x=cx, y=int(h * 0.7))

    def _select_time(self, mins):
        self.study_minutes = mins
        for m, btn in self._preset_btns.items():
            if m == mins:
                btn.config(fg="#120921", bg=styles.PURPLE_GLOW)
            else:
                btn.config(fg="#4a3a6a", bg="#1a0f2e")

    def _change_rounds(self, delta):
        self.rounds_goal = max(1, min(8, self.rounds_goal + delta))
        self.rounds_display.config(text=str(self.rounds_goal))
        if hasattr(self, '_break_info'):
            self._break_info.config(
                text=f"5 min breaks  ·  15 min long break after {self.rounds_goal} rounds"
            )

    # ── Session flow ──────────────────────────────────────────────────────────

    def _start_session(self):
        self.root.unbind("<Configure>") 
        self._clear_ui()
        self.current_round = 0
        self.is_break = False
        self._begin_study()

    def _begin_study(self):
        self.is_break = False
        self._launch_timer(self.study_minutes * 60, label="FOCUS")

    def _begin_break(self):
        self.is_break = True
        if self.current_round >= self.rounds_goal:
            secs = self.long_break_mins * 60
            label = "LONG BREAK"
        else:
            secs = self.short_break_mins * 60
            label = "SHORT BREAK"
        self._launch_timer(secs, label=label)

    def _launch_timer(self, total_secs, label="FOCUS"):
        self.total_seconds = total_secs
        self.seconds_left = total_secs
        self.is_running = True
        self.is_paused = False

        color = "#00cccc" if self.is_break else styles.PURPLE_GLOW
        self.canvas.itemconfig(self.clock_display, fill=color)
        self.canvas.itemconfig(self.session_label_id, text=label, fill=color)
        self._update_round_label()
        self._show_clock()
        self._draw_timer_visuals()
        self._show_controls()
        self._draw_progress_bar()
        self.root.bind("<Configure>", self._on_timer_resize)  #for resizing
        self._tick()

    # ── Tick ──────────────────────────────────────────────────────────────────

    def _tick(self):
        if not self.is_running or self.is_paused:
            return
        if self.seconds_left >= 0:
            mins, secs = divmod(self.seconds_left, 60)
            self.canvas.itemconfig(self.clock_display, text=f"{mins:02d}:{secs:02d}")
            self._update_ring()
            self._draw_progress_bar()
            self.seconds_left -= 1
            self.after_id = self.root.after(1000, self._tick)
        else:
            self._handle_cycle()

    def _handle_cycle(self):
        if not self.is_break:
            self.current_round += 1
            self._update_round_label()
            self._begin_break()
        else:
            if self.current_round >= self.rounds_goal:
                self.current_round = 0
            self._begin_study()

    # ── Controls ──────────────────────────────────────────────────────────────
    def _show_controls(self):
        for widget, win_id in self.ui_widgets:
            try:
                self.canvas.delete(win_id)
                widget.destroy()
            except Exception:
                pass
        self.ui_widgets.clear()
        self._draw_nav_bar()
    
        w, h = self._wh()
        cx = w // 2
    
        ctrl_frame = tk.Frame(self.root, bg="#0a0514")
        self.pause_btn = tk.Label(
            ctrl_frame, text="⏸",
            font=("Courier New", 22),
            fg="#a78bfa", bg="#0a0514",
            cursor="hand2", padx=12
        )
        self.pause_btn.pack(side="left")
        self.pause_btn.bind("<Button-1>", lambda e: self._toggle_pause())
        reset_btn = tk.Label(
            ctrl_frame, text="↺",
            font=("Courier New", 22),
            fg="#a78bfa", bg="#0a0514",
            cursor="hand2", padx=12
        )
        reset_btn.pack(side="left")
        reset_btn.bind("<Button-1>", lambda e: self.show_setup())
        skip_btn = tk.Label(
            ctrl_frame, text="⏭",
            font=("Courier New", 22),
            fg="#a78bfa", bg="#0a0514",
            cursor="hand2", padx=12
        )
        skip_btn.pack(side="left")
        skip_btn.bind("<Button-1>", lambda e: self._skip())
        self._place(ctrl_frame, x=cx, y=int(h * 0.80))
    
        tasks_btn = tk.Label(
            self.root, text="[Open Tasks List]",
            font=("Cinzel", 10),
            fg="#6b4c8a", bg="#0a0514",
            cursor="hand2", padx=6
        )
        tasks_btn.bind("<Enter>", lambda e: tasks_btn.config(fg=styles.PURPLE_GLOW))
        tasks_btn.bind("<Leave>", lambda e: tasks_btn.config(fg="#6b4c8a"))
        tasks_btn.bind("<Button-1>", lambda e: self.app.task_manager.open())
        self._place(tasks_btn, x=cx, y=int(h * 0.87))
    
    def _toggle_pause(self):
        if self.is_paused:
            self.is_paused = False
            self.pause_btn.config(text="⏸")
            self._tick()
        else:
            self.is_paused = True
            self.pause_btn.config(text="▶")
            if self.after_id:
                self.root.after_cancel(self.after_id)

    def _skip(self):
        if self.after_id:
            self.root.after_cancel(self.after_id)
        if not self.is_break:
            self.current_round += 1
            self._update_round_label()
            self._begin_break()
        else:
            if self.current_round >= self.rounds_goal:
                self.current_round = 0
            self._begin_study()

    # ── Visuals ───────────────────────────────────────────────────────────────

    def _draw_timer_visuals(self):
        self.canvas.delete("timer_bg")
        w = self.canvas.winfo_width() or 512
        h = self.canvas.winfo_height() or 512
        cx, cy = w // 2, h // 2
        s = self._scale()
    
        # Scale fonts
        self.canvas.itemconfig(self.session_label_id, font=("Cinzel", max(8, int(11 * s)), "bold"))
        self.canvas.itemconfig(self.clock_display,    font=("Courier New", max(24, int(52 * s)), "bold"))
        self.canvas.itemconfig(self.round_label_id,   font=("Cinzel", max(8, int(11 * s))))
    
        # Scale oval :3
        r = int(91 * s)
        self.canvas.create_oval(
            cx - r, cy - r, cx + r, cy + r,
            fill="#0b0514", outline="",
            tags=("timer_bg", "timer_elements")
        )
    
        # Scale image
        if not self.center_image or self._last_scale != s:
            self._last_scale = s
            self._load_monkey(size=int(200 * s))
        if self.center_image:
            self.canvas.create_image(
                cx, cy, image=self.center_image,
                tags=("timer_bg", "timer_elements")
            )
    
        # Scale text positions
        self.canvas.coords(self.session_label_id, cx, cy - int(65 * s))
        self.canvas.coords(self.clock_display,    cx, cy - int(10 * s))
        self.canvas.coords(self.round_label_id,   cx, cy + int(55 * s))
    
        self.canvas.tag_raise(self.session_label_id)
        self.canvas.tag_raise(self.clock_display)
        self.canvas.tag_raise(self.round_label_id)

    def _load_monkey(self):
        try:
            img = Image.open("visuals/images/monkey.jpg").convert("RGBA")
            img = img.resize((200, 200), Image.Resampling.LANCZOS)
            datas = img.getdata()
            newData = []
            for item in datas:
                if item[0] < 40 and item[1] < 40 and item[2] < 40:
                    newData.append((0, 0, 0, 0))
                else:
                    newData.append((item[0], item[1], item[2], 100))
            img.putdata(newData)
            self.center_image = ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Image Error: {e}")

    def _update_ring(self):
        w = self.canvas.winfo_width() or 512
        h = self.canvas.winfo_height() or 512
        cx, cy = w // 2, h // 2
        r = 100

        extent = (self.seconds_left / self.total_seconds) * 359.9 if self.total_seconds > 0 else 0
        color = "#00cccc" if self.is_break else styles.PURPLE_GLOW
        self.canvas.delete("timer_ring")
        self.canvas.create_arc(
            cx - r, cy - r, cx + r, cy + r,
            start=90, extent=extent,
            outline=color, width=8,
            style="arc",
            tags=("timer_ring", "timer_elements")
        )
        self.canvas.tag_raise(self.session_label_id)
        self.canvas.tag_raise(self.clock_display)
        self.canvas.tag_raise(self.round_label_id)

    def _update_round_label(self):
        text = f"Round {self.current_round + 1} / {self.rounds_goal}"
        self.canvas.itemconfig(self.round_label_id, text=text)

     # ── Resize ───────────────────────────────────────────────────────────────
    
    def _on_timer_resize(self, event):
        if event.widget != self.root:
            return
        if self._resize_id:
            self.root.after_cancel(self._resize_id)
        self._resize_id = self.root.after(80, self._redraw_timer)

    def _redraw_timer(self):
        self._resize_id = None
        self._draw_timer_visuals()
        self._update_ring()
        self._show_controls()

    def _scale(self):
        w = self.canvas.winfo_width() or 512
        h = self.canvas.winfo_height() or 512
        return min(w, h) / 512  # 512 is your base size
