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
        try: 
            # stop loop if window is closed
            if not self.root.winfo_exists():
                return
                
            idle_time = round(self.monitor.get_idle_time())
            current_app, window_title = self.monitor.get_active_info() #from monitor.py
            curent_app = current_app.lower() # update both to be lowercase, case sensitive
            window_title = window_title.lower()
    
            # ADD THIS LINE TO DEBUG:
            print(f"I see you are using: {current_app}")
            
            lecture_apps = ["chrome", "safari", "preview", "zoom", "spotify", "music", "bcourses"] # Ones that get an exception if studying 
            distraction_sites = ["youtube", "netflix", "twitter", "instagram", "tiktok", "ebay", "etsy", "reddit", "messages"]
    
            # Exceptions check -- berkeley, school, lecture, etc. or music
            exception = any(word in window_title.lower() for word in 
                            ["berkeley", "cal", "school", "lecture", "cs", "compsci", "polysci", "ds", "data science", "datasci", 
                             "classical", "music", "lofi", "instrumental"])
            
            is_distraction = any(site in window_title for site in distraction_sites) and not exception
    
            # Update if idle, UNLESS user is actively studying
            if current_app in lecture_apps and not is_distraction:
                threshold = 1800 # 30 mins
                self.status_label.config(text="Lecture Mode 🎓", fg="blue")
            else:
                threshold = 300 # 5 min
                self.status_label.config(text="Flowing... 🌊", fg="green")
    
            if idle_time > threshold:
                self.status_label.config(text="Lock in gamers!", fg="red")
                
            self.root.after(500, self.update_ui) # Update afterwards
    except (tk.TclError, Exception):
            # If the window is closed, exit loop
            return

if __name__ == "__main__":
    root = tk.Tk()
    app = FlowApp(root)
    root.mainloop()
