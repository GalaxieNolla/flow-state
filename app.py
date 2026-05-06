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
from modules.arcane import Arcane
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
        self.canvas = tk.Canvas(root, highlightthickness=0, bd=0, bg="#0a0514")
        self.canvas.pack(fill="both", expand=True)
        self.root.configure(bg="#0a0514")
        self.canvas.configure(bg="#0a0514")
        self.canvas.all_refs = [] # properly initialize

        # Background
        self.bg_image = ImageTk.PhotoImage(
            Image.open("visuals/arcane background.webp").resize((512, 512))
        )
        self.bg_item = self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")
        self.root.bind("<Configure>", self._on_resize, add=True)

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
        self.lb_btn, self.lb_txt, self.lb_active, self.lb_inactive, self.lb_base, self.lb_cur = create_mode_button(
            self.canvas, 256, 180, "Leaderboard", self.leaderboard.open, 340, 130
        )
        self.time_btn, self.time_txt, self.time_active, self.time_inactive, self.time_base, self.time_cur = create_mode_button(
            self.canvas, 140, 260, "Time-Based", lambda: self.enter_timer_mode(), 290, 130
        )
        self.task_btn, self.task_txt, self.task_active, self.task_inactive, self.task_base, self.task_cur = create_mode_button(
            self.canvas, 372, 260, "Task-Based", lambda: self.task_manager.open(), 290, 130
        )
        self.btn_images = {
            'lb':   {'active': None, 'inactive': None},
            'time': {'active': None, 'inactive': None},
            'task': {'active': None, 'inactive': None},
        }

        # Create runes beneath the time & task buttons
        self.mc_time = Arcane(self.canvas, self.time_btn, self.time_txt, color="blue")
        self.mc_task = Arcane(self.canvas, self.task_btn, self.task_txt, color="purple")

        # Titles
        self.sub_title_label = self.canvas.create_text(
            256, 80,
            text="We are entering ...",
            font=("Cinzel", 12, "bold"),
            fill="#402867"
        )
        self.main_title_label = self.canvas.create_text(
            256, 100,
            text="Flow State",
            font=("Cinzel", 50, "bold"),
            fill="#ddd1ff"
        )
        
        # Mode selction
        self.select_label_win = self.canvas.create_text(
            256, 300,
            text="Select a mode...",
            font=("Cinzel", 20, "bold"),
            fill="#febdff"
        )

        # Footer toggle
        self.mode_toggle_id = self.canvas.create_text(
            256, 490,
            text="switch mode",
            font=("Georgia", 8, "italic"),
            fill="#b2d2fc"
        )
        self.canvas.tag_bind(self.mode_toggle_id, "<Button-1>",
            lambda e: self.enter_timer_mode() if self.is_task_mode else self.task_manager.open())
        self.canvas.tag_bind(self.mode_toggle_id, "<Enter>",
            lambda e: self.canvas.itemconfig(self.mode_toggle_id, fill="#c37aff"))
        self.canvas.tag_bind(self.mode_toggle_id, "<Leave>",
            lambda e: self.canvas.itemconfig(self.mode_toggle_id, fill="#7a7a7a"))

        self.update_ui()

        # Force correct sizing on launch
        self.root.after(50, lambda: self._on_resize(type('E', (), {
            'widget': self.root, 'width': self.root.winfo_width(), 'height': self.root.winfo_height()
        })()))

    # ── Navigation ────────────────────────────────────────────────────────────

    def enter_timer_mode(self):
        """
        Switch to timer setup view.
        """
        self.is_task_mode = False        
        self._set_main_menu_visible(False) # Hide main landing page buttons
        self.canvas.itemconfig(self.dim_overlay, state="normal") # Dim background
        self.canvas.tag_raise(self.dim_overlay)
        
        self.timer_manager.show_setup() # Display timer UI

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
        for item in [self.lb_btn, self.lb_txt, #leaderboard
                     self.time_btn, self.time_txt, #time
                     self.task_btn, self.task_txt]: #task
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
        self.canvas.all_refs = [] # clear 
        # DEBUG print(f"ROOT: {w}x{h} | CANVAS: {self.canvas.winfo_width()}x{self.canvas.winfo_height()}")

        self.canvas.config(width=w, height=h) #can remove this line w/o any resizing errors (?)
        
        # Background
        img = Image.open("visuals/arcane background.webp").resize((w, h), Image.Resampling.LANCZOS)
        self.bg_image = ImageTk.PhotoImage(img)
        self.canvas.itemconfig(self.bg_item, image=self.bg_image)
        self.canvas.coords(self.bg_item, 0, 0) # essentially, left corner = pivot 
        self.canvas.coords(self.dim_overlay, 0, 0, w, h)
    
        # Button positions — defined FIRST so _rescale_btn can use them
        cx = w // 2
        lb_x,   lb_y   = cx,              int(h * 0.15)
        time_x, time_y = int(w * 0.27),   int(h * 0.28)
        task_x, task_y = int(w * 0.73),   int(h * 0.28)
    
        def _rescale_btn(bg_id, txt_id, active_pil, inactive_pil, base_size, current_size, x, y, key):
            scale = h / 650
            # update sizing
            current_size[0] = max(160, int(base_size[0] * scale)) #recall size was in format (width, height) --> [0] = width
            current_size[1] = max(50,  int(base_size[1] * scale))
            inactive_i = ImageTk.PhotoImage(inactive_pil.resize((current_size[0], current_size[1]), Image.Resampling.LANCZOS))
            active_i   = ImageTk.PhotoImage(active_pil.resize((current_size[0], current_size[1]), Image.Resampling.LANCZOS))
            
            # Store current resized images
            self.btn_images[key]['active']   = active_i
            self.btn_images[key]['inactive'] = inactive_i
            
            self.canvas.itemconfig(bg_id, image=inactive_i)
            self.canvas.coords(bg_id, x, y)
            self.canvas.coords(txt_id, x, y)
            font_size = max(14, int(30 * scale))
            self.canvas.itemconfig(txt_id, font=("Cinzel", font_size, "bold"))
            self.canvas.all_refs.extend([inactive_i, active_i])
            
        _rescale_btn(self.lb_btn,   self.lb_txt,   self.lb_active,   self.lb_inactive,   self.lb_base,   self.lb_cur,   lb_x,   lb_y,   'lb')
        _rescale_btn(self.time_btn, self.time_txt, self.time_active, self.time_inactive, self.time_base, self.time_cur, time_x, time_y, 'time')
        _rescale_btn(self.task_btn, self.task_txt, self.task_active, self.task_inactive, self.task_base, self.task_cur, task_x, task_y, 'task')
            
        self.canvas.coords(self.select_label_win, cx, int(h * 0.42))
        self.canvas.coords(self.mode_toggle_id, cx, int(h * 0.92))

if __name__ == "__main__":
    root = tk.Tk()
    app = FlowApp(root)
    root.protocol("WM_DELETE_WINDOW", lambda: [app.session_tracker.save_session(), root.destroy()])
    root.mainloop()
