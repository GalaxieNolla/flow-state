import tkinter as tk
from monitor import ActivityMonitor

class FlowApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Flow State")
        self.root.geometry("400x200")
        self.root.attributes("-topmost", True)

        self.monitor = ActivityMonitor()
        
        self.status_label = tk.Label(root, text="Flowing...", font=("Helvetica", 24))
        self.status_label.pack(pady=10)

        self.app_label = tk.Label(root, text="Detecting app...", font=("Helvetica", 12), fg="gray")
        self.app_label.pack(pady=5)

        self.update_ui()

    def update_ui(self):
        idle_time = self.monitor.get_idle_time()
        current_app = self.monitor.get_active_app()
        
        self.app_label.config(text=f"Current App: {current_app}")
        
        if idle_time > 10:
            self.status_label.config(text="Focus! ⚡️", fg="red")
        else:
            self.status_label.config(text="Flowing... 🌊", fg="green")
            
        self.root.after(1000, self.update_ui)

if __name__ == "__main__":
    root = tk.Tk()
    app = FlowApp(root)
    root.mainloop()
