import tkinter as tk
from monitor import ActivityMonitor

class FlowApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Flow State")
        self.root.geometry("300x150")
        self.root.attributes("-topmost", True) # Keeps window on top

        self.monitor = ActivityMonitor()
        
        self.label = tk.Label(root, text="Flowing...", font=("Helvetica", 24))
        self.label.pack(expand=True)

        self.update_ui()

    def update_ui(self):
        idle_time = self.monitor.get_idle_time()
        
        if idle_time > 10:
            self.label.config(text="Focus! ⚡️", fg="red")
        else:
            self.label.config(text="Flowing... 🌊", fg="green")
            
        # Refresh the UI every 1 second
        self.root.after(1000, self.update_ui)

if __name__ == "__main__":
    root = tk.Tk()
    app = FlowApp(root)
    root.mainloop()
