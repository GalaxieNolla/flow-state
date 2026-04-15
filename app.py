import tkinter as tk
from monitor import ActivityMonitor
from PIL import Image, ImageTk  # for images
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
        self.leaderboard = Leaderboard(self.root)

        # create canvas
        self.canvas = tk.Canvas(root, width=512, height=512, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.leaderboard_btn = create_mode_button(self.canvas, 256, 220, "Leaderboard", self.leaderboard.open)

        # load & display image
        self.bg_image = ImageTk.PhotoImage(Image.open("visuals/arcane background.webp").resize((512, 512)))
        self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")

        self.status_label = tk.Label(root, text="Select a mode...", font=("Helvetica", 22, "bold italic"), bg="#120921", fg="#c37aff", highlightthickness=0)
        # OPT: try out bg="#110820", fg="#c37aff" if want to change colors
        self.canvas.create_window(256, 256, window=self.status_label)

        # set up containers
        self.main_container = tk.Frame(self.root, bg="#120921")
        self.main_container.pack(fill="both", expand=True)
        
        # Refer to modules
        self.task_manager = TaskSticky(self.root)
        self.timer_manager = StudyTimer(self.root, self.status_label, self.main_container, self.canvas)

        # switch modes
        '''self.mode_toggle = tk.Button(root, text="switch mode", font=("Helvetica", 10, "italic"), command=lambda: self.set_mode(not self.is_task_mode),
                                     bd=0, bg="#110820", fg="#7a7a7a",
                                     activebackground="#110820", activeforeground="#c37aff", highlightthickness=0)
        self.canvas.create_window(256, 490, window=self.mode_toggle)'''
        self.mode_toggle = tk.Label(root, text="switch mode", font=styles.FONT_FOOTER)
        styles.apply_ghost_style(self.mode_toggle, command=lambda: self.set_mode(not self.is_task_mode))
        self.canvas.create_window(256, 490, window=self.mode_toggle)

        # Set up buttons
        self.leaderboard_btn = create_mode_button(self.canvas, 256, 100, "Leaderboard", self.leaderboard.open) #top center
        self.time_btn = create_mode_button(self.canvas, 140, 220, "Time-Based", lambda: self.set_mode(False)) #side by side
        self.task_btn = create_mode_button(self.canvas, 372, 220, "Task-Based", lambda: self.set_mode(True))

        # Update
        self.update_button_colors()
        self.update_ui()

    def set_mode(self, mode_bool):
        self.is_task_mode = mode_bool
        self.update_button_colors()
        
        if self.is_task_mode:
            self.status_label.pack_forget()
            self.canvas.create_window(256, 256, window=self.status_label) 
            self.task_manager.open()
        else:
            self.setup_time_mode() 
            
        current = "task-based" if self.is_task_mode else "time-based"
        self.mode_toggle.config(text=f"switch mode (current: {current})", fg="#7a7a7a")

    def setup_time_mode(self):
        # clear main container
        self.main_container.pack_forget() 
        
        # move status to bottom
        self.status_label.pack_forget() 
        self.status_label.config(font=("Helvetica", 14, "italic")) # Slightly smaller for the bottom
        self.status_label.pack(side="bottom", pady=20)

        self.timer_manager.show_setup()
    
    def update_button_colors(self):
        pass
            
    def toggle_logic(self):
        self.set_mode(not self.is_task_mode)
            
    def update_ui(self):
        self.root.after(500, self.update_ui) # Update afterwards
        try: 
            # stop loop if window is closed
            if not self.root.winfo_exists():
                return
                
            idle_time = round(self.monitor.get_idle_time())
            current_app, window_title = self.monitor.get_active_info() #from monitor.py
            current_app = str(current_app).lower() # update both to be lowercase str, case sensitive
            window_title = str(window_title).lower()
    
            # ADD THIS LINE TO DEBUG: -- see if the monitor detects your 'distractions'
            # print(f"I see you are using: {current_app}")
            
            distraction_sites = ["youtube", "netflix", "twitter", "instagram", "tiktok", "ebay", "etsy", "reddit", "messages", "discord"]
    
            # Exceptions check -- berkeley, school, lecture, etc. or music
            exception = any(word in window_title.lower() for word in 
                            ["berkeley", "cal", "school", "lecture", "cs", "compsci", "polysci", "ds", "data science", "datasci", 
                             "classical", "music", "lofi", "instrumental", "spotify", "bcourses", "zoom", "pomodoro"])
            
            is_distraction = any(site in current_app for site in distraction_sites) or any(site in window_title for site in distraction_sites)

            if is_distraction and not exception:
                site_name = next((s for s in distraction_sites if s in window_title or s in current_app), "this site")
                self.nudge.show(site_name)
                if not self.nudge.is_distracted:  # only count new distractions
                    self.session_tracker.record_distraction()
            else:
                self.nudge.hide()
                
        except Exception as e:
            print(f"Internal Error: {e}") # This lets you see the error in terminal instead of freezing
            return

if __name__ == "__main__":
    root = tk.Tk()
    app = FlowApp(root)
    root.protocol("WM_DELETE_WINDOW", lambda: [app.session_tracker.save_session(), root.destroy()])
    root.mainloop()
