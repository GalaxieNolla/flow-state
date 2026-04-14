import tkinter as tk
from monitor import ActivityMonitor
from PIL import Image, ImageTk  # for images
from task_module import TaskSticky
from timer_module import StudyTimer
import os 

class FlowApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Flow State")
        self.root.geometry("512x512")
        self.root.attributes("-topmost", True)
        self.monitor = ActivityMonitor()
        self.is_task_mode = False

        # Image --------
        img = Image.open("arcane background.webp").resize((512, 512))
        self.bg_image = ImageTk.PhotoImage(img)

        self.canvas = tk.Canvas(root, width=512, height=512, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")
        
        # BUTTON -------
        self.header_label = tk.Label(root, text="Choose your studying method today:", font=("Helvetica", 14), bg="#120921", fg="#c37aff") #Give users a choice on what to use
        self.canvas.create_window(256, 40, window=self.header_label)
        
        btn_frame = tk.Frame(root, bg="#1a0b2e")
        self.time_btn = tk.Button(btn_frame, text="Time-Based", width=15, command=lambda: self.set_mode(False)) #time
        self.time_btn.pack(side="left", padx=5)
        self.task_btn = tk.Button(btn_frame, text="Task-Based", width=15, command=lambda: self.set_mode(True)) # task button
        self.task_btn.pack(side="left", padx=5)
        self.canvas.create_window(256, 80, window=btn_frame)

        self.status_label = tk.Label(root, text="Select a mode...", font=("Helvetica", 22, "bold italic"), bg="#120921", fg="#c37aff", highlightthickness=0)
        # OPT: try out bg="#110820", fg="#c37aff" if want to change colors
        self.canvas.create_window(256, 256, window=self.status_label)

        # Refer to modules
        self.task_manager = TaskSticky(self.root)
        self.timer_manager = StudyTimer(self.root, self.status_label)

        # switch modes
        '''self.mode_toggle = tk.Button(root, text="switch mode", font=("Helvetica", 10, "italic"), command=lambda: self.set_mode(not self.is_task_mode),
                                     bd=0, bg="#1a0b2e", fg="gray", activebackground="#110820", activeforeground="#c37aff",
                                     highlightthickness=0)
        self.canvas.create_window(256, 480, window=self.mode_toggle)'''

        self.mode_toggle = tk.Button(root, text="switch mode", font=("Helvetica", 10, "italic"), command=lambda: self.set_mode(not self.is_task_mode),
                                     bd=0, bg="#110820", fg="#7a7a7a",
                                     activebackground="#110820", activeforeground="#c37aff", highlightthickness=0)
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
        purple, blue, grey = "#c37aff", "#4069c9", "#7a7a7a"
        if self.is_task_mode:
            self.task_btn.config(highlightbackground=purple, highlightthickness=3)
            self.time_btn.config(highlightbackground=grey, highlightthickness=1)
        else:
            self.time_btn.config(highlightbackground=blue, highlightthickness=3)
            self.task_btn.config(highlightbackground=grey, highlightthickness=1)
            
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
                self.status_label.config(text="Lock in gamers!! 💪", fg="red")
            else:
                self.status_label.config(text=status_text, fg=status_color)
                
        except Exception as e:
            print(f"Internal Error: {e}") # This lets you see the error in terminal instead of freezing
            return

if __name__ == "__main__":
    root = tk.Tk()
    app = FlowApp(root)
    root.mainloop()
