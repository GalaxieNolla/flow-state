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
        self.root.geometry("512x512")
        self.root.attributes("-topmost", True)

        self.monitor = ActivityMonitor()
        self.is_task_mode = False
        self.nudge = Nudge(self.root, self.monitor)
        self.session_tracker = SessionTracker(self.monitor, self.nudge)
        self.session_tracker.start(self.root)
        self.leaderboard = Leaderboard(self.root, self.session_tracker)

        # ── Canvas ────────────────────────────────────────────────────────────
        self.canvas = tk.Canvas(root, width=512, height=512, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Background
        self.bg_image = ImageTk.PhotoImage(
            Image.open("visuals/arcane background.webp").resize((512, 512))
        )
        self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")

        # Dim overlay (when in timer time :3)
        self.dim_overlay = self.canvas.create_rectangle(
            0, 0, 512, 512,
            fill="#0a0514", stipple="gray50",
            state="hidden"
        )

        # ── Modules ───────────────────────────────────────────────────────────
        self.task_manager = TaskSticky(self.root)
        self.timer_manager = StudyTimer(self.root, self.canvas, self)

        # ── Main Menu Buttons ─────────────────────────────────────────────────
        self.leaderboard_btn_id = create_mode_button(
            self.canvas, 256, 100, "Leaderboard", self.leaderboard.open
        )
        self.time_btn_id = create_mode_button(
            self.canvas, 140, 180, "Time-Based", lambda: self.enter_timer_mode()
        )
        self.task_btn_id = create_mode_button(
            self.canvas, 372, 180, "Task-Based", lambda: self.task_manager.open()
        )

        # Mode selction
        self.select_label = tk.Label(
            root, text="Select a mode...",
            font=("Cinzel", 18, "bold"),
            bg="#120921", fg="#c37aff",
            highlightthickness=0
        )
        self.select_label_win = self.canvas.create_window(256, 280, window=self.select_label)

        # Footer toggle
        self.mode_toggle = tk.Label(
            root, text="switch mode", font=styles.FONT_FOOTER
        )
        styles.apply_ghost_style(
            self.mode_toggle,
            command=lambda: self.enter_timer_mode() if self.is_task_mode else self.task_manager.open()
        )
        self.canvas.create_window(256, 490, window=self.mode_toggle)

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

        self.mode_toggle.config(text="switch mode (current: time-based)", fg="#7a7a7a")

    def return_to_menu(self):
        """
        Return to main menu from timer
        """
        self.timer_manager.stop()
        self.canvas.itemconfig(self.dim_overlay, state="hidden") #restore overlap
        self._set_main_menu_visible(True) #display main menu

        self.mode_toggle.config(text="switch mode", fg="#7a7a7a")

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

if __name__ == "__main__":
    root = tk.Tk()
    app = FlowApp(root)
    root.protocol("WM_DELETE_WINDOW", lambda: [app.session_tracker.save_session(), root.destroy()])
    root.mainloop()
