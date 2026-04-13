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

        self.app_label = tk.Label(root, text="Detecting app: ", font=("Helvetica", 12), fg="gray")
        self.app_label.pack(pady=5)

        self.timer_label = tk.Label(root, text="Idle: 0s", font=("Helvetica", 12), fg="gray")
        self.timer_label.pack(pady=5)

        self.update_ui()

    def update_ui(self):
        idle_time = self.monitor.get_idle_time()
        current_app, window_title = self.monitor.get_active_info() #from monitor.py

        lecture_apps = ["Google Chrome", "Safari", "Preview", "Zoom"] # Ones that get an exception if studying 
        is_distraction = "YouTube" in window_title or "Netflix" in window_title
        
        self.app_label.config(text=f"Current App: {current_app}")
        self.timer_label.config(text=f"Idle: {idle_time}s")

        # Update if idle, UNLESS user is actively studying
        if current_app in lecture_apps and not is_distraction:
            threshold = 1800 # 30 mins
            self.status_label.config(text="Lecture Mode 🎓", fg="blue")
        else:
            threshold = 10
            self.status_label.config(text="Flowing... 🌊", fg="green")

        if idle_time > threshold:
            self.status_label.config(text="Focus! ⚡️", fg="red")
            
        self.root.after(500, self.update_ui) # Update afterwards

if __name__ == "__main__":
    root = tk.Tk()
    app = FlowApp(root)
    root.mainloop()
