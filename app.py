import tkinter as tk
from monitor import ActivityMonitor

class FlowApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Flow State")
        self.root.geometry("400x200")
        self.root.attributes("-topmost", True)

        self.monitor = ActivityMonitor()
        
        self.status_label = tk.Label(root, text="Entering flow state...", font=("Helvetica", 24))
        self.status_label.pack(pady=10)
        
        self.update_ui()

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
            
            is_distraction = any(site in current_app for site in distraction_sites) and not exception or \
                 any(site in window_title for site in distraction_sites) and not exception
    
            # Update if idle, UNLESS user is actively studying
            if is_distraction and not exception:
                threshold = 10 # 10 seconds, trigger immediately
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
