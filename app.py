import tkinter as tk
from monitor import ActivityMonitor
from PIL import Image, ImageTk
from visuals import styles
from modules.task_module import TaskSticky
from modules.timer_module import StudyTimer
from modules.custom_buttons import create_mode_button
from modules.nudge import Nudge
from modules.session_tracker import SessionTracker
from modules.leaderboard import Leaderboard
import os

class FlowApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Flow State")
        self.root.attributes("-topmost", True)
        self.root.minsize(500, 400) #must be smaller

        self.monitor = ActivityMonitor()
        self.is_task_mode = False
        self.nudge = Nudge(self.root, self.monitor)
        self.session_tracker = SessionTracker(self.monitor, self.nudge)
        self.session_tracker.start(self.root)
        self.leaderboard = Leaderboard(self.root, self.session_tracker)

        # ── Canvas ────────────────────────────────────────────────────────────
        self.canvas = tk.Canvas(root, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Background
        self.bg_image = ImageTk.PhotoImage(
            Image.open("visuals/arcane background.webp").resize((512, 512))
        )
        self.bg_item = self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")
        self.root.bind("<Configure>", self._on_resize)

        # Dim overlay (when in timer time :3)
        self.dim_overlay = self.canvas.create_rectangle(
            0, 0, 512, 512,
            fill="#0a0514", stipple="gray75",
            state="hidden"
        )

        # ── Modules ───────────────────────────────────────────────────────────
        self.task_manager = TaskSticky(self.root)
        self.timer_manager = StudyTimer(self.root, self.canvas, self)

        # ── Main Menu Buttons ─────────────────────────────────────────────────
        self.leaderboard_btn_id, self.leaderboard_txt_id, self.leaderboard_active_pil, self.leaderboard_inactive_pil, self.leaderboard_base_size = create_mode_button(
            self.canvas, 256, 100, "Leaderboard", self.leaderboard.open, 300, 90 #larger width bc longer word
        )
        self.time_btn_id, self.time_txt_id, self.time_active_pil, self.time_inactive_pil, self.time_base_size = create_mode_button(
            self.canvas, 140, 180, "Time-Based", lambda: self.enter_timer_mode(), 270, 90
        )
        self.task_btn_id, self.task_txt_id, self.task_active_pil, self.task_inactive_pil, self.task_base_size = create_mode_button(
            self.canvas, 372, 180, "Task-Based", lambda: self.task_manager.open(), 270, 90
        )

        # Mode selction
        self.select_label_win = self.canvas.create_text(
            256, 280,
            text="Select a mode...",
            font=("Cinzel", 18, "bold"),
            fill="#c37aff"
        )

        # Footer toggle
        self.mode_toggle_id = self.canvas.create_text(
            256, 490,
            text="switch mode",
            font=styles.FONT_FOOTER,
            fill="#7a7a7a"
        )
        self.canvas.tag_bind(self.mode_toggle_id, "<Button-1>",
            lambda e: self.enter_timer_mode() if self.is_task_mode else self.task_manager.open())
        self.canvas.tag_bind(self.mode_toggle_id, "<Enter>",
            lambda e: self.canvas.itemconfig(self.mode_toggle_id, fill="#c37aff"))
        self.canvas.tag_bind(self.mode_toggle_id, "<Leave>",
            lambda e: self.canvas.itemconfig(self.mode_toggle_id, fill="#7a7a7a"))

        self.update_ui()

    # ── Navigation ────────────────────────────────────────────────────────────

    def enter_timer_mode(self):
        """
        Switch to timer setup view.
        """
        self.is_task_mode = False

        # Hide main landing page buttons
        self._set_main_menu_visible(False)

        # Dim background
        self.canvas.itemconfig(self.dim_overlay, state="normal")
        self.canvas.tag_raise(self.dim_overlay)

        # Display timer UI
        self.timer_manager.show_setup()

        self.canvas.itemconfig(self.mode_toggle_id, text="switch mode (current: time-based)")

    def return_to_menu(self):
        """
        Return to main menu from timer
        """
        self.timer_manager.stop()
        self.canvas.itemconfig(self.dim_overlay, state="hidden") #restore overlap
        self._set_main_menu_visible(True) #display main menu

        self.canvas.itemconfig(self.mode_toggle_id, text="switch mode")

    def _set_main_menu_visible(self, visible):
        state = "normal" if visible else "hidden"
        for tag in ["btn_140_180", "btn_372_180", "btn_256_100"]:
            for item in self.canvas.find_withtag(tag):
                self.canvas.itemconfig(item, state=state)
        self.canvas.itemconfig(self.select_label_win, state=state)

    # ── UI Loop ───────────────────────────────────────────────────────────────

    def update_ui(self):
        self.root.after(500, self.update_ui)
        try:
            if not self.root.winfo_exists():
                return
            distraction = self.monitor.is_distraction()
            if distraction:
                if not self.nudge.is_distracted:
                    self.session_tracker.record_distraction()
                    self.nudge.show(distraction)
            else:
                self.nudge.hide()
        except Exception:
            import traceback
            traceback.print_exc()
    
    # ── MISC ──────────────────────────────────────────────────────────────────

    def _on_resize(self, event):
        if event.widget != self.root:
            return
        w, h = event.width, event.height
    
        # Background
        img = Image.open("visuals/arcane background.webp").resize((w, h), Image.Resampling.LANCZOS)
        self.bg_image = ImageTk.PhotoImage(img)
        self.canvas.itemconfig(self.bg_item, image=self.bg_image)
        self.canvas.coords(self.dim_overlay, 0, 0, w, h)
    
        # Button positions — defined FIRST so _rescale_btn can use them
        cx = w // 2
        lb_x,   lb_y   = cx,              int(h * 0.15)
        time_x, time_y = int(w * 0.27),   int(h * 0.28)
        task_x, task_y = int(w * 0.73),   int(h * 0.28)
    
        def _rescale_btn(bg_id, txt_id, active_pil, inactive_pil, base_size, x, y):
            scale = h / 650
            w_px = max(160, int(base_size[0] * scale))
            h_px = max(50,  int(base_size[1] * scale))
            inactive_i = ImageTk.PhotoImage(inactive_pil.resize((w_px, h_px), Image.Resampling.LANCZOS))
            active_i   = ImageTk.PhotoImage(active_pil.resize((w_px, h_px), Image.Resampling.LANCZOS))
            self.canvas.itemconfig(bg_id, image=inactive_i)
            self.canvas.coords(bg_id, x, y)
            self.canvas.coords(txt_id, x, y)
            self.canvas.all_refs.extend([inactive_i, active_i])
    
        _rescale_btn(self.leaderboard_btn_id, self.leaderboard_txt_id,
                     self.leaderboard_active_pil, self.leaderboard_inactive_pil,
                     self.leaderboard_base_size, lb_x, lb_y)
        _rescale_btn(self.time_btn_id, self.time_txt_id,
                     self.time_active_pil, self.time_inactive_pil,
                     self.time_base_size, time_x, time_y)
        _rescale_btn(self.task_btn_id, self.task_txt_id,
                     self.task_active_pil, self.task_inactive_pil,
                     self.task_base_size, task_x, task_y)
    
        self.canvas.coords(self.select_label_win, cx, int(h * 0.42))
        self.canvas.coords(self.mode_toggle_id, cx, int(h * 0.92))

if __name__ == "__main__":
    root = tk.Tk()
    app = FlowApp(root)
    root.protocol("WM_DELETE_WINDOW", lambda: [app.session_tracker.save_session(), root.destroy()])
    root.mainloop()
