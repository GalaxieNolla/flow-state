import tkinter as tk

class TaskSticky:
    def __init__(self, root):
        self.root = root
        self.window = None
        self.tasks = []
        self.task_font = ("Helvetica", 18)
        self.done_font = ("Helvetica", 18, "overstrike") #strikethrough

    def open(self):
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return

        self.window = tk.Toplevel(self.root)
        self.window.title("Tasks")
        self.window.geometry("300x400")
        self.window.configure(bg="#120921")
        self.window.attributes("-topmost", True)

        # for each new task
        self.entry = tk.Entry(
            self.window, 
            font=self.task_font, 
            bg="#1b0d31", 
            fg="white", 
            bd=0, 
            highlightthickness=1,
            highlightbackground="#c37aff"
        )
        self.entry.pack(fill="x", padx=10, pady=10)
        self.entry.bind("<Return>", lambda e: self.add_task())

        self.list_frame = tk.Frame(self.window, bg="#120921")
        self.list_frame.pack(fill="both", expand=True)

    def add_task(self):
        text = self.entry.get()
        if text:
            label = tk.Label(
                self.list_frame, 
                text=text, 
                font=self.task_font, 
                fg="white", 
                bg="#120921",
                anchor="w",
                padx=10,
                pady=5,
                cursor="hand2"
            )
            label.pack(fill="x")
            
            # Click to toggle strike-through
            label.bind("<Button-1>", lambda e, l=label: self.toggle_strike(l))
            self.entry.delete(0, tk.END)

    def toggle_strike(self, label):
        current_font = label.cget("font")
        # Toggle between normal and overstrike
        if "overstrike" in str(current_font):
            label.config(font=self.task_font, fg="white")
        else:
            label.config(font=self.done_font, fg="#7a7a7a")
