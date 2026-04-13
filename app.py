import tkinter as tk
from monitor import ActivityMonitor

class FlowApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Flow State")
        self.root.geometry("400x250")
        self.root.attributes("-topmost", True)

        self.monitor = ActivityMonitor()
        self.is_task_mode = False

        # BUTTON -------
        tk.Label(root, text="Choose your studying method today:", font=("Helvetica", 14)).pack(pady=10) #Give users a choice on what to use
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=5)

        self.time_btn = tk.Button(btn_frame, text="Time-Based", width=15, command=lambda: self.set_mode(False)) #time
        self.time_btn.pack(side="left", padx=5)
        self.task_btn = tk.Button(btn_frame, text="Task-Based", width=15, command=lambda: self.set_mode(True)) # task button
        self.task_btn.pack(side="left", padx=5)

        self.status_label = tk.Label(root, text="Select a mode...", font=("Helvetica", 20))
        self.status_label.pack(pady=20)

        # switch modes
        self.mode_toggle = tk.Button(root, text="switch mode", font=("Helvetica", 10, "italic"), command=self.toggle_logic, bd=0, fg="gray")
        self.mode_toggle.pack(side="bottom", pady=10)

        # Update
        self.update_button_colors()
        self.update_ui()

    def set_mode(self, mode_bool):
        self.is_task_mode = mode_bool
        self.update_button_colors()

        # Update the footer text to show current status
        current = "task-based" if self.is_task_mode else "time-based"
        self.mode_toggle.config(text=f"switch mode (current: {current})")

    def update_button_colors(self):
        if self.is_task_mode:
            self.task_btn.config(bg="gray", relief="sunken")
            self.time_btn.config(bg="systemButtonFace", relief="raised")
        else:
            self.time_btn.config(bg="gray", relief="sunken")
            self.task_btn.config(bg="systemButtonFace", relief="raised")

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
                status_text, status_color = "Lock in gamers!! 💪", "red"
            elif current_app in lecture_apps or exception:
                threshold = 1800 # 30 mins
                status_text, status_color = "We love an academic queen 💎", "blue"
            else:
                threshold = 300 # 5 min
                status_text, status_color = "We in the flow state 💃", "blue"

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
