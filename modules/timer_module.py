import tkinter as tk
from visuals import styles
from PIL import Image, ImageTk

class StudyTimer:
    def __init__(self, root, status_label, container, canvas):
        self.root = root
        self.status_label = status_label
        self.container = container
        self.canvas = canvas

        # Timer state
        self.seconds_left = 0
        self.total_seconds = 0
        self.is_break = False
        self.is_running = False
        self.is_paused = False
        self.after_id = None
        self.center_image = None
        self.ui_widgets = []  # track widgets

        # Pomodoro config (defaults)
        self.study_minutes = 25
        self.rounds_goal = 4
        self.current_round = 0  # completed study rounds

        # Short break = 5min, long break = 15min (standard)
        self.short_break_mins = 5
        self.long_break_mins = 15

        # Canvas items
        self.clock_display = self.canvas.create_text(
            256, 356, text="",
            font=("Courier New", 52, "bold"),
            fill=styles.PURPLE_GLOW,
            state="hidden"
        )
        self.session_label_id = self.canvas.create_text(
            256, 295, text="",
            font=("Cinzel", 12, "bold"),
            fill="#a78bfa",
            state="hidden"
        )
        self.round_dots_id = self.canvas.create_text(
            256, 415, text="",
            font=("Cinzel", 16),
            fill=styles.PURPLE_GLOW,
            state="hidden"
        )

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _place(self, widget, **kwargs):
        """Place a widget on canvas and track it for cleanup."""
        win_id = self.canvas.create_window(**kwargs, window=widget)
        self.ui_widgets.append((widget, win_id))
        return win_id

    def _clear_ui(self):
        """Remove all setup/control widgets from canvas."""
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

    def _hide_canvas_items(self):
        self.canvas.itemconfig(self.clock_display, state="hidden")
        self.canvas.itemconfig(self.session_label_id, state="hidden")
        self.canvas.itemconfig(self.round_dots_id, state="hidden")

    def _show_canvas_items(self):
        self.canvas.itemconfig(self.clock_display, state="normal")
        self.canvas.itemconfig(self.session_label_id, state="normal")
        self.canvas.itemconfig(self.round_dots_id, state="normal")

    # ── Setup Screen ──────────────────────────────────────────────────────────

    def show_setup(self):
        """Setup screen: preset time + rounds selector."""
        self._clear_ui()
        self._hide_canvas_items()
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self.is_running = False
        self.is_paused = False
        self.current_round = 0

        # ── Study time label
        time_label = tk.Label(
            self.root, text="STUDY TIME",
            font=("Cinzel", 10, "bold"),
            bg="#120921", fg="#6b4c8a"
        )
        self._place(time_label, x=256, y=270)

        # ── Preset time buttons
        preset_frame = tk.Frame(self.root, bg="#120921")
        presets = [15, 25, 45, 60]
        self.selected_time = tk.IntVar(value=self.study_minutes)

        for mins in presets:
            is_sel = mins == self.study_minutes
            btn = tk.Label(
                preset_frame,
                text=f"{mins}",
                font=("Cinzel", 15, "bold"),
                fg=styles.PURPLE_GLOW if is_sel else "#4a3a6a",
                bg="#1e0f33" if is_sel else "#120921",
                width=3, pady=4,
                relief="flat",
                cursor="hand2"
            )
            btn.pack(side="left", padx=4)
            btn.bind("<Button-1>", lambda e, m=mins, b=btn: self._select_time(m))

        self._preset_btns = {m: preset_frame.winfo_children()[i] for i, m in enumerate(presets)}
        self._place(preset_frame, x=256, y=305)

        # ── Rounds label
        rounds_label = tk.Label(
            self.root, text="ROUNDS",
            font=("Cinzel", 10, "bold"),
            bg="#120921", fg="#6b4c8a"
        )
        self._place(rounds_label, x=256, y=340)

        # ── Rounds selector
        rounds_frame = tk.Frame(self.root, bg="#120921")

        minus_btn = tk.Label(rounds_frame, text="−", font=("Cinzel", 18, "bold"),
                             fg="#a78bfa", bg="#120921", cursor="hand2", padx=8)
        minus_btn.pack(side="left")
        minus_btn.bind("<Button-1>", lambda e: self._change_rounds(-1))

        self.rounds_display = tk.Label(rounds_frame, text=str(self.rounds_goal),
                                       font=("Cinzel", 18, "bold"),
                                       fg=styles.PURPLE_GLOW, bg="#120921", width=2)
        self.rounds_display.pack(side="left")

        plus_btn = tk.Label(rounds_frame, text="+", font=("Cinzel", 18, "bold"),
                            fg="#a78bfa", bg="#120921", cursor="hand2", padx=8)
        plus_btn.pack(side="left")
        plus_btn.bind("<Button-1>", lambda e: self._change_rounds(1))

        self._place(rounds_frame, x=256, y=370)

        # ── Break info line
        break_info = tk.Label(
            self.root,
            text=f"5 min breaks · long break after {self.rounds_goal} rounds",
            font=("Cinzel", 9, "italic"),
            bg="#120921", fg="#4a3a6a"
        )
        self._break_info_label = break_info
        self._place(break_info, x=256, y=398)

        # ── Start button
        start_btn = tk.Label(
            self.root, text="▶  START",
            font=("Cinzel", 13, "bold"),
            fg="#120921", bg=styles.PURPLE_GLOW,
            padx=18, pady=6,
            cursor="hand2"
        )
        start_btn.bind("<Button-1>", lambda e: self._start_session())
        start_btn.bind("<Enter>", lambda e: start_btn.config(bg="#b06eff"))
        start_btn.bind("<Leave>", lambda e: start_btn.config(bg=styles.PURPLE_GLOW))
        self._place(start_btn, x=256, y=435)

    def _select_time(self, mins):
        self.study_minutes = mins
        for m, btn in self._preset_btns.items():
            if m == mins:
                btn.config(fg=styles.PURPLE_GLOW, bg="#1e0f33")
            else:
                btn.config(fg="#4a3a6a", bg="#120921")

    def _change_rounds(self, delta):
        self.rounds_goal = max(1, min(8, self.rounds_goal + delta))
        self.rounds_display.config(text=str(self.rounds_goal))
        if hasattr(self, '_break_info_label'):
            self._break_info_label.config(
                text=f"5 min breaks · long break after {self.rounds_goal} rounds"
            )

    # ── Session Start ─────────────────────────────────────────────────────────

    def _start_session(self):
        """Begin the first study round."""
        self._clear_ui()
        self.current_round = 0
        self.is_break = False
        self._begin_study()

    def _begin_study(self):
        self.is_break = False
        secs = self.study_minutes * 60
        self._launch_timer(secs, label="FOCUS")

    def _begin_break(self):
        self.is_break = True
        # Long break after completing all rounds
        if self.current_round >= self.rounds_goal:
            secs = self.long_break_mins * 60
            label = f"LONG BREAK"
        else:
            secs = self.short_break_mins * 60
            label = "SHORT BREAK"
        self._launch_timer(secs, label=label)

    def _launch_timer(self, total_secs, label="FOCUS"):
        self.total_seconds = total_secs
        self.seconds_left = total_secs
        self.is_running = True
        self.is_paused = False

        # Update session label color
        if self.is_break:
            self.canvas.itemconfig(self.session_label_id, fill="#00cccc")
            self.canvas.itemconfig(self.clock_display, fill="#00cccc")
        else:
            self.canvas.itemconfig(self.session_label_id, fill="#a78bfa")
            self.canvas.itemconfig(self.clock_display, fill=styles.PURPLE_GLOW)

        self.canvas.itemconfig(self.session_label_id, text=label)
        self._show_canvas_items()
        self._update_round_dots()
        self._draw_visuals()
        self._show_controls()
        self._tick()

    # ── Tick ──────────────────────────────────────────────────────────────────

    def _tick(self):
        if not self.is_running or self.is_paused:
            return
        if self.seconds_left >= 0:
            mins, secs = divmod(self.seconds_left, 60)
            self.canvas.itemconfig(self.clock_display, text=f"{mins:02d}:{secs:02d}")
            self._update_ring()
            self.seconds_left -= 1
            self.after_id = self.root.after(1000, self._tick)
        else:
            self._handle_cycle()

    def _handle_cycle(self):
        if not self.is_break:
            # Completed a study round
            self.current_round += 1
            self._update_round_dots()
            if self.current_round >= self.rounds_goal:
                # All rounds done — long break then reset
                self._begin_break()
            else:
                self._begin_break()
        else:
            # Break finished
            if self.current_round >= self.rounds_goal:
                # After long break, reset everything
                self.current_round = 0
            self._begin_study()

    # ── Controls ──────────────────────────────────────────────────────────────

    def _show_controls(self):
        """Show pause/reset/skip buttons below the ring."""
        # Clear any existing controls
        for widget, win_id in self.ui_widgets:
            try:
                self.canvas.delete(win_id)
                widget.destroy()
            except Exception:
                pass
        self.ui_widgets.clear()

        ctrl_frame = tk.Frame(self.root, bg="#120921")

        # Pause/Resume
        self.pause_btn = tk.Label(
            ctrl_frame, text="⏸",
            font=("Courier New", 20),
            fg="#a78bfa", bg="#120921",
            cursor="hand2", padx=10
        )
        self.pause_btn.pack(side="left")
        self.pause_btn.bind("<Button-1>", lambda e: self._toggle_pause())

        # Reset
        reset_btn = tk.Label(
            ctrl_frame, text="↺",
            font=("Courier New", 20),
            fg="#a78bfa", bg="#120921",
            cursor="hand2", padx=10
        )
        reset_btn.pack(side="left")
        reset_btn.bind("<Button-1>", lambda e: self.show_setup())

        # Skip
        skip_btn = tk.Label(
            ctrl_frame, text="⏭",
            font=("Courier New", 20),
            fg="#a78bfa", bg="#120921",
            cursor="hand2", padx=10
        )
        skip_btn.pack(side="left")
        skip_btn.bind("<Button-1>", lambda e: self._skip())

        self._place(ctrl_frame, x=256, y=455)

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
        """Skip current session (study → break or break → study)."""
        if self.after_id:
            self.root.after_cancel(self.after_id)
        if not self.is_break:
            self.current_round += 1
            self._update_round_dots()
            self._begin_break()
        else:
            if self.current_round >= self.rounds_goal:
                self.current_round = 0
            self._begin_study()

    # ── Visuals ───────────────────────────────────────────────────────────────

    def _draw_visuals(self):
        """Draw the dark circle background behind the clock."""
        self.canvas.delete("timer_bg")
        self.canvas.create_oval(
            165, 265, 347, 447,
            fill="#0b0514", outline="",
            tags=("timer_bg", "timer_elements")
        )
        if not self.center_image:
            self._load_monkey()
        if self.center_image:
            self.canvas.create_image(
                256, 356, image=self.center_image,
                tags=("timer_bg", "timer_elements")
            )
        self.canvas.tag_raise(self.clock_display)
        self.canvas.tag_raise(self.session_label_id)
        self.canvas.tag_raise(self.round_dots_id)

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
        extent = (self.seconds_left / self.total_seconds) * 359.9 if self.total_seconds > 0 else 0
        color = "#00cccc" if self.is_break else styles.PURPLE_GLOW
        self.canvas.delete("timer_ring")
        self.canvas.create_arc(
            156, 256, 356, 456,
            start=90, extent=extent,
            outline=color, width=8,
            style="arc",
            tags=("timer_ring", "timer_elements")
        )
        self.canvas.tag_raise(self.clock_display)
        self.canvas.tag_raise(self.session_label_id)
        self.canvas.tag_raise(self.round_dots_id)

    def _update_round_dots(self):
        """Show dots: filled for completed rounds, empty for remaining."""
        filled = "●" * self.current_round
        empty = "○" * max(0, self.rounds_goal - self.current_round)
        self.canvas.itemconfig(self.round_dots_id, text=filled + empty)
