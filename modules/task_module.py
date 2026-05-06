import tkinter as tk
import json
import os

saved_sticky = os.path.join(os.path.dirname(__file__), "tasks.json")

class TaskSticky:
    def __init__(self, root):
        self.root = root
        self.window = None
        self.input_frame = None
        self.font_normal = ("Cinzel", 18)
        self.font_done = ("Cinzel", 18, "overstrike") # for strikethrough
        self.instruction_font = ("Cinzel", 10, "italic") # for instructions :3

        # priority sorting
        self.priority_levels = ["None", "Low", "Medium", "High"]
        self.priority_colors = {
            "None": {"bullet": "#c37aff", "bg": "#120921", "entry_fg": "#c37aff"},
            "Low": {"bullet": "#5bc8af", "bg": "#0f2a28", "entry_fg": "#8eded0"},
            "Medium": {"bullet": "#e8825a", "bg": "#2a1a0f", "entry_fg": "#f5aa88"},
            "High": {"bullet": "#d45a8a", "bg": "#2a0f1a", "entry_fg": "#f598bb"},
            "LongTerm": {"bullet": "#b381d3", "bg": "#2a1f33", "entry_fg": "#dcb5ff"},
        }

    def open(self):
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return

        self.window = tk.Toplevel(self.root)
        self.window.title("Tasks")
        self.window.geometry("350x450")
        self.window.configure(bg="#120921")
        self.window.attributes("-topmost", True)

        # Main container 
        self.main_container = tk.Frame(self.window, bg="#120921")
        self.main_container.pack(fill="both", expand=True, padx=5, pady=15)

        # Load when open
        self.load_tasks()
        self.setup_input_line()

        def _global_right_click(e):
            print("RIGHT CLICK HIT", e.widget, type(e.widget))
            widget = e.widget
            row = widget if isinstance(widget, tk.Frame) and not getattr(widget, 'is_placeholder', False) else getattr(widget, 'master', None)
            print("ROW FOUND:", row, "in get_task_rows:", row in self.get_task_rows() if row else "N/A")
            if row and isinstance(row, tk.Frame) and row != self.input_frame and not getattr(row, 'is_placeholder', False) and row in self.get_task_rows():
                row.destroy()
                self.save_tasks()
        
        self.window.bind("<Button-2>", _global_right_click)
        
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)  # save when closed

        # footnote instructions for task to-do list
        self.instruction_label = tk.Label(
            self.window,
            text="[Delete: Right-click task • Complete: Left-click bullet]",
            font=("Georgia", 10, "italic"),
            fg="#6b4c8a",
            bg="#120921",
            pady=5
        )
        self.instruction_label.pack(side="bottom", fill="x")

    def save_tasks(self):
        tasks = []
        for row in self.main_container.winfo_children():
            if (self.input_frame is not None and row == self.input_frame) or not isinstance(row, tk.Frame):
                continue
            if getattr(row, 'is_placeholder', False):
                continue
            for widget in row.winfo_children():
                if isinstance(widget, tk.Entry):
                    text = widget.get().strip()
                    done = "overstrike" in str(widget.cget("font"))
                    priority = getattr(row, "priority", "None")
                    if text:
                        tasks.append({"text": text, "done": done, "priority": priority})
        with open(saved_sticky, "w") as f:
            json.dump(tasks, f)

    def load_tasks(self):
        if not os.path.exists(saved_sticky):
            return
        with open(saved_sticky, "r") as f:
            tasks = json.load(f)
        for task in tasks:
            self.create_task_row(task["text"], done=task.get("done", False), priority=task.get("priority", "None"))

    def on_close(self):
        print("Saving tasks...")
        self.save_tasks()
        self.window.destroy()

    def setup_input_line(self):
        self.input_frame = tk.Frame(self.main_container, bg="#120921")
        self.input_frame.pack(fill="x", side="top", pady=5)

        plus_label = tk.Label(self.input_frame, text=" +", font=self.font_normal, fg="#c37aff", bg="#120921")
        plus_label.pack(side="left", padx=(5, 10))

        self.new_entry = tk.Entry(self.input_frame, font=self.font_normal, bg="#120921",
                                  fg="#c37aff", bd=0, insertbackground="white",
                                  highlightthickness=1, highlightbackground="#c37aff", highlightcolor="#c37aff")
        self.new_entry.pack(side="left", fill="x", expand=True, padx=(0, 15))
        self.new_entry.focus_set()

        self.new_entry.bind("<Return>", lambda e: self.commit_task())

    def commit_task(self):
        text = self.new_entry.get().strip()
        if not text:
            return
        self.input_frame.destroy()
        self.create_task_row(text)
        self.setup_input_line()

    def create_task_row(self, text, done=False, priority="None"):
        row = tk.Frame(self.main_container, bg=self.priority_colors[priority]["bg"])
        row.pack(fill="x", side="top", pady=2)

        row.bind("<Enter>", lambda e, r=row: r.config(cursor="hand2"))
        row.bind("<Leave>", lambda e, r=row: r.config(cursor=""))

        row.priority = priority
        row.task_text = text

        # Bullet (left)
        bullet_btn = tk.Label(row, text="○", font=("Cinzel", 22),
                              fg=self.priority_colors[priority]["bullet"],
                              bg=self.priority_colors[priority]["bg"],
                              cursor="hand2", padx=5, pady=5)
        bullet_btn.pack(side="left", padx=(5, 10))

        # Entry (middle)
        task_edit = tk.Entry(row, font=self.font_normal, bg=self.priority_colors[priority]["bg"],
                     fg=self.priority_colors[priority]["entry_fg"], bd=0,
                     insertbackground="white", highlightthickness=0)
        row.task_edit = task_edit
        task_edit.insert(0, text)
        task_edit.pack(side="left", fill="x", expand=True, padx=(0, 10))
        task_edit.row = row

        # Priority selector (right)
        priority_btn = tk.Label(row, text=f"▼ {priority}", font=("Cinzel", 9, "bold"),
                                fg="#a78bfa", bg=self.priority_colors[priority]["bg"],
                                cursor="hand2", padx=5)
        priority_btn.pack(side="right", padx=(0, 10))
        priority_btn.current = priority
        priority_btn.row = row

        # ── Bindings ──────────────────────────────────────────────────────────

        # Strikethrough w/ left-click
        bullet_btn.bind("<Button-1>", lambda e: self.toggle_strike(task_edit, bullet_btn, row))

        priority_btn.bind("<Button-1>", lambda e, r=row, btn=priority_btn: self.cycle_priority(r, btn))

        # Drag
        row.bind("<Button-1>", lambda e, r=row: self.start_drag(e, r))
        task_edit.bind("<B1-Motion>", lambda e, r=row: self.start_drag(e, r)) #hopefully fix binding issue for delete

        # Save on focus out
        task_edit.bind("<FocusOut>", lambda e: self.on_edit_finish(task_edit))

        # Hover highlight
        task_edit.bind("<Enter>", lambda e: task_edit.config(highlightthickness=1, highlightbackground="#a78bfa"))
        task_edit.bind("<Leave>", lambda e: task_edit.config(highlightthickness=0))

        if done:
            self.toggle_strike(task_edit, bullet_btn, row)

    # ── Drag & Drop ────────────────────────────────────────────────────────────

    def start_drag(self, event, row):
        """Record start position. Ghost/placeholder created only after threshold."""
        self.drag_row = row
        self.drag_start_y = event.y_root
        self.drag_active = False
        self.drag_ghost = None
        self.drag_placeholder = None
        self.drag_insert_idx = None

        self.window.bind("<B1-Motion>", self.on_drag_global)
        self.window.bind("<ButtonRelease-1>", self.end_drag_global)
        return "break"

    def _ensure_drag_active(self, row):
        """Lazily create ghost and placeholder on first real motion."""
        if self.drag_active:
            return
        self.drag_active = True

        # Placeholder: dark purple gap shown where row will land
        self.drag_placeholder = tk.Frame(self.main_container, bg="#2a1060",
                                         height=row.winfo_height() or 44)
        self.drag_placeholder.is_placeholder = True  # so get_task_rows() skips

        # Ghost
        text = row.task_edit.get() if hasattr(row, 'task_edit') else ""
        colors = self.priority_colors[row.priority]
        win_width = self.window.winfo_width() - 10
        win_x = self.window.winfo_rootx() + 5

        self.drag_ghost = tk.Toplevel(self.window)
        self.drag_ghost.overrideredirect(True)
        self.drag_ghost.attributes("-alpha", 0.80)
        self.drag_ghost.attributes("-topmost", True)

        tk.Label(
            self.drag_ghost, text=text,
            font=self.font_normal,
            fg=colors["entry_fg"], bg=colors["bg"],
            anchor="w", padx=20, pady=8
        ).pack(fill="x")

        self.drag_ghost.geometry(f"{win_width}x44+{win_x}+{self.drag_start_y - 22}")

    def _move_ghost(self, y_root):
        if self.drag_ghost and self.drag_ghost.winfo_exists():
            win_x = self.window.winfo_rootx() + 5
            win_width = self.window.winfo_width() - 10
            self.drag_ghost.geometry(f"{win_width}x44+{win_x}+{y_root - 22}")

    def on_drag_global(self, event):
        if not hasattr(self, 'drag_row') or self.drag_row is None:
            return

        if not self.drag_active and abs(event.y_root - self.drag_start_y) < 8:
            return

        self._ensure_drag_active(self.drag_row)
        self._move_ghost(event.y_root)

        rows = self.get_task_rows()
        if self.drag_row not in rows:
            return

        other_rows = [r for r in rows if r is not self.drag_row]
        container_top = self.main_container.winfo_rooty()
        mouse_y = event.y_root - container_top

        # Determine insert position based on midpoints of other rows
        insert_idx = len(other_rows)
        for i, r in enumerate(other_rows):
            mid = r.winfo_y() + r.winfo_height() // 2
            if mouse_y < mid:
                insert_idx = i
                break

        # Skip full repack if position hasn't changed
        if insert_idx == self.drag_insert_idx:
            return
        self.drag_insert_idx = insert_idx

        # Unpack everything, repack with placeholder at insert position
        self.drag_row.pack_forget()
        self.drag_placeholder.pack_forget()
        for r in other_rows:
            r.pack_forget()

        for i, r in enumerate(other_rows):
            if i == insert_idx:
                self.drag_placeholder.pack(fill="x", side="top", pady=2)
            r.pack(fill="x", side="top", pady=2)
        if insert_idx >= len(other_rows):
            self.drag_placeholder.pack(fill="x", side="top", pady=2)

        if self.input_frame:
            self.input_frame.pack_forget()
            self.input_frame.pack(fill="x", side="top", pady=5)

        return "break"

    def end_drag_global(self, event):
        if not hasattr(self, 'drag_row') or self.drag_row is None:
            return

        if self.drag_active:
            rows = self.get_task_rows()
            insert_idx = self.drag_insert_idx if self.drag_insert_idx is not None else len(rows)
            other_rows = [r for r in rows if r is not self.drag_row]

            self.drag_placeholder.pack_forget()
            self.drag_row.pack_forget()
            for r in other_rows:
                r.pack_forget()

            for i, r in enumerate(other_rows):
                if i == insert_idx:
                    self.drag_row.pack(fill="x", side="top", pady=2)
                r.pack(fill="x", side="top", pady=2)
            if insert_idx >= len(other_rows):
                self.drag_row.pack(fill="x", side="top", pady=2)

            if self.drag_ghost and self.drag_ghost.winfo_exists():
                self.drag_ghost.destroy()

            if self.input_frame:
                self.input_frame.pack_forget()
                self.input_frame.pack(fill="x", side="top", pady=5)

            self.save_tasks()

        self.cleanup_drag()
        return "break"

    def cleanup_drag(self):
        self.drag_row = None
        self.drag_active = False
        self.drag_ghost = None
        self.drag_placeholder = None
        self.drag_insert_idx = None
        self.drag_start_y = None
        self.window.unbind("<B1-Motion>")
        self.window.unbind("<ButtonRelease-1>")

    def get_task_rows(self):
        """Return task rows, excluding input frame and drag placeholder."""
        rows = []
        for child in self.main_container.winfo_children():
            if not isinstance(child, tk.Frame):
                continue
            if self.input_frame is not None and child == self.input_frame:
                continue
            if getattr(child, 'is_placeholder', False):
                continue
            rows.append(child)
        return rows

    # ── Priority ───────────────────────────────────────────────────────────────

    def cycle_priority(self, row, btn):
        """Cycle priority: None -> Low -> Medium -> High -> None"""
        current = row.priority
        levels = self.priority_levels
        next_idx = (levels.index(current) + 1) % len(levels)
        new_priority = levels[next_idx]
        row.priority = new_priority
        is_striked = "overstrike" in str(row.task_edit.cget("font")) if hasattr(row, 'task_edit') else False
        btn.config(text=f"▼ {new_priority}")

        colors = self.priority_colors[new_priority]
        row.config(bg=colors["bg"])

        if is_striked:
            text_color = self.darken_color(colors["entry_fg"], 0.4)
            bullet_color = self.darken_color(colors["bullet"], 0.4)
        else:
            text_color = colors["entry_fg"]
            bullet_color = colors["bullet"]

        for child in row.winfo_children():
            if isinstance(child, tk.Label):
                if child.cget("text") in ("○", "●"):
                    child.config(fg=bullet_color, bg=colors["bg"])
                else:
                    child.config(bg=colors["bg"])
            elif isinstance(child, tk.Entry):
                child.config(bg=colors["bg"], fg=text_color)

        btn.config(bg=colors["bg"])
        self.save_tasks()

    def darken_color(self, hex_color, factor=0.3):
        """Return desaturated/darkened version for completed tasks."""
        hex_color = hex_color.lstrip('#')
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        grey = int(r * 0.299 + g * 0.587 + b * 0.114)
        # paint mixing <3
        r = int(r * factor + grey * (1 - factor))
        g = int(g * factor + grey * (1 - factor))
        b = int(b * factor + grey * (1 - factor))
        return f"#{r:02x}{g:02x}{b:02x}"

    def toggle_strike(self, entry_widget, circle_widget, row):
        """Toggle strikethrough. Striked text/bullet become darkened priority color."""
        current_font = entry_widget.cget("font")
        priority = getattr(row, "priority", "None")
        original_fg = self.priority_colors[priority]["entry_fg"]
        original_bullet = self.priority_colors[priority]["bullet"]
        grey_color = self.darken_color(original_fg, 0.4)

        if "overstrike" in str(current_font):
            entry_widget.config(font=self.font_normal, fg=original_fg)
            circle_widget.config(text="○", fg=original_bullet)
        else:
            entry_widget.config(font=self.font_done, fg=grey_color)
            circle_widget.config(text="●", fg=grey_color)

    def on_edit_finish(self, widget):
        if not widget.get().strip():
            widget.master.destroy()
