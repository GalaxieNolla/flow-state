import tkinter as tk

class TaskSticky:
    def __init__(self, parent_root):
        self.root = parent_root

    def open(self):
        # Semi-transparent window
        self.win = tk.Toplevel(self.root)
        self.win.title("Tasks")
        self.win.geometry("220x300+50+100")
        self.win.attributes("-alpha", 0.85, "-topmost", True)
        self.win.config(bg="#1a0b2e")

        # Entry for new tasks
        self.entry = tk.Entry(self.win, bg="#c37aff", fg="white", 
                              insertbackground="white", bd=0)
        self.entry.pack(pady=10, padx=10, fill="x")
        self.entry.bind("<Return>", lambda e: self.add_task())

        tk.Button(self.win, text="＋", command=self.add_task, 
                  bg="#1a0b2e", fg="#c37aff", bd=0).pack()

    def add_task(self):
        task_text = self.entry.get()
        if task_text:
            btn = tk.Button(self.win, text=task_text, bg="#1a0b2e", fg="#c37aff", 
                            font=("Helvetica", 11), anchor="w", bd=0, padx=10)
            # Strike-through logic
            btn.config(command=lambda b=btn: b.config(text=f"✓ {b['text']}", 
                                                      fg="#7a7a7a", state="disabled"))
            btn.pack(fill="x")
            self.entry.delete(0, 'end')
