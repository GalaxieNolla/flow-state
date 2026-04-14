import tkinter as tk

class TaskSticky:
    def __init__(self, parent_root):
        self.root = parent_root

    def open(self):
        self.win = tk.Toplevel(self.root)
        self.win.title("Tasks")
        self.win.geometry("250x400")
        self.win.attributes("-alpha", 0.9, "-topmost", True)
        self.win.config(bg="#1a0b2e")
        
        # Container for the list
        self.list_frame = tk.Frame(self.win, bg="#1a0b2e")
        self.list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.render_input_row()

    def render_input_row(self):
        # Create a row with [+] and an Entry
        self.input_frame = tk.Frame(self.list_frame, bg="#1a0b2e")
        self.input_frame.pack(fill="x", pady=2)
        
        tk.Label(self.input_frame, text="＋", fg="#c37aff", bg="#1a0b2e").pack(side="left")
        
        self.entry = tk.Entry(self.input_frame, bg="#1a0b2e", fg="white", 
                              insertbackground="white", bd=0, highlightthickness=0)
        self.entry.pack(side="left", fill="x", expand=True, padx=5)
        self.entry.focus_set()
        self.entry.bind("<Return>", lambda e: self.add_task())

    def add_task(self):
        txt = self.entry.get()
        if not txt: return
        
        # Remove the current input row to put the task there
        self.input_frame.destroy()
        
        # Add the completed task line
        task_row = tk.Button(self.list_frame, text=f"  {txt}", fg="#c37aff", bg="#1a0b2e",
                             activeforeground="gray", activebackground="#1a0b2e",
                             font=("Helvetica", 11), anchor="w", bd=0, highlightthickness=0)
        task_row.config(command=lambda b=task_row: b.config(text=f"  ✓ {txt}", fg="#444", state="disabled"))
        task_row.pack(fill="x")
        
        # Re-render input row at the bottom
        self.render_input_row()
