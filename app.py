import tkinter as tk
from monitor import ActivityMonitor
from PIL import Image, ImageTk  # for images
from visuals import styles
from modules.task_module import TaskSticky
from modules.timer_module import StudyTimer
from modules.custom_buttons import create_mode_button
import os

class FlowApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Flow State")
        self.root.geometry("512x512")
        self.root.attributes("-topmost", True)
        self.monitor = ActivityMonitor()
        self.is_task_mode = False

        # create canvas
        self.canvas = tk.Canvas(root, width=512, height=512, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # load & display image
        self.bg_image = ImageTk.PhotoImage(Image.open("visuals/arcane background.webp").resize((512, 512)))
        self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")

        self.status_label = tk.Label(root, text="Select a mode...", font=("Helvetica", 22, "bold italic"), bg="#120921", fg="#c37aff", highlightthickness=0)
        # OPT: try out bg="#110820", fg="#c37aff" if want to change colors
        self.canvas.create_window(256, 256, window=self.status_label)

        # Refer to modules
        self.task_manager = TaskSticky(self.root)
        self.timer_manager = StudyTimer(self.root, self.status_label)

        # switch modes
        '''self.mode_toggle = tk.Button(root, text="switch mode", font=("Helvetica", 10, "italic"), command=lambda: self.set_mode(not self.is_task_mode),
                                     bd=0, bg="#110820", fg="#7a7a7a",
                                     activebackground="#110820", activeforeground="#c37aff", highlightthickness=0)
        self.canvas.create_window(256, 490, window=self.mode_toggle)'''
        self.mode_toggle = tk.Label(root, text="switch mode", font=styles.FONT_FOOTER)
        styles.apply_ghost_style(self.mode_toggle, command=lambda: self.set_mode(not self.is_task_mode))
        self.canvas.create_window(256, 490, window=self.mode_toggle)

        # Update
        self.update_button_colors()
        self.update_ui()

    def set_mode(self, mode_bool):
        self.is_task_mode = mode_bool
        self.update_button_colors()
        
        if self.is_task_mode:
            self.task_manager.open()
        else:
            self.timer_manager.start(25, 5) # Default 25/5
            
        current = "task-based" if self.is_task_mode else "time-based"
        self.mode_toggle.config(text=f"switch mode (current: {current})", fg="#7a7a7a")

    def update_button_colors(self):
        active_purple = "#2A1440" 
        if self.is_task_mode:
            self.task_btn.config(bg=styles.PURPLE_BUTTON, fg=styles.PURPLE_GLOW)
            self.time_btn.config(bg=styles.BG_DARK, fg="white")
        else:
            self.time_btn.config(bg=styles.PURPLE_BUTTON, fg=styles.CYAN_FOG)
            self.task_btn.config(bg=styles.BG_DARK, fg="white")
            
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
            current_app = current_app.lower() # update both to be lowercase, case sensitive
            window_title = window_title.lower()
    
            # ADD THIS LINE TO DEBUG:
            print(f"I see you are using: {current_app}")
            
            lecture_apps = ["chrome", "safari", "preview", "zoom", "spotify", "music", "bcourses"] # Ones that get an exception if studying 
            distraction_sites = ["youtube", "netflix", "twitter", "instagram", "tiktok", "ebay", "etsy", "reddit", "messages"]
    
            # Exceptions check -- berkeley, school, lecture, etc. or music
            exception = any(word in window_title.lower() for word in 
                            ["berkeley", "cal", "school", "lecture", "cs", "compsci", "polysci", "ds", "data science", "datasci", 
                             "classical", "music", "lofi", "instrumental"])
            
            is_distraction = any(site in current_app for site in distraction_sites) or any(site in window_title for site in distraction_sites)
    
            # Update if idle, UNLESS user is actively studying
            if is_distraction and not exception:
                threshold = 0 if self.is_task_mode else 10 # 10 seconds
                status_text, status_color = "Lock in gamers!! 💪", "#ff4b4b" # Vivid Red
            elif current_app in lecture_apps or exception:
                threshold = 1800 # 30 mins
                status_text, status_color = "We love an academic queen 💎", "#40c9c9" # Cyan fog
            else:
                threshold = 300 # 5 min
                status_text, status_color = "We in the flow state 💃", "#c37aff" # Neon Purple

            # If idle time too long
            if idle_time > threshold:
                self.status_label.config(text="Lock in gamers!! 💪", fg=styles.RED_LOCKIN)
            else:
                self.status_label.config(text=status_text, fg=status_color)
                
        except Exception as e:
            print(f"Internal Error: {e}") # This lets you see the error in terminal instead of freezing
            return

if __name__ == "__main__":
    root = tk.Tk()
    app = FlowApp(root)
    root.mainloop()
