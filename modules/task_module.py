import tkinter as tk

class TaskSticky:
    def __init__(self, root):
        self.root = root
        self.window = None
        self.font_normal = ("Helvetica", 18)
        self.font_done = ("Helvetica", 18, "overstrike") # for strikethrough

    def open(self):
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return

        self.window = tk.Toplevel(self.root)
        self.window.title("Tasks")
        self.window.geometry("350x450")
        self.window.configure(bg="#120921")
        self.window.attributes("-topmost", True)

        # Main container that holds the growing list
        self.main_container = tk.Frame(self.window, bg="#120921")
        self.main_container.pack(fill="both", expand=True, padx=5, pady=15)

        self.setup_input_line()

    def setup_input_line(self):
        # Pack to main_container so it stays relative to the tasks
        self.input_frame = tk.Frame(self.main_container, bg="#120921")
        self.input_frame.pack(fill="x", side="top", pady=5)

        plus_label = tk.Label(self.input_frame, text="+", font=self.font_normal, fg="#c37aff", bg="#120921", width=3)
        plus_label.pack(side="left", padx=(5, 15))

        self.new_entry = tk.Entry(self.input_frame, font=self.font_normal, bg="#120921", 
                                  fg="#c37aff", bd=0, insertbackground="white",
                                  highlightthickness=1, highlightbackground="#c37aff", highlightcolor="#c37aff")
        self.new_entry.pack(side="left", fill="x", expand=True)
        self.new_entry.focus_set()
        
        self.new_entry.bind("<Return>", lambda e: self.commit_task())

    def commit_task(self):
        text = self.new_entry.get().strip()
        if not text:
            return

        self.input_frame.destroy() # Remove old +
        self.create_task_row(text) # Add row to the container
        self.setup_input_line()    # New + dir under row

    def create_task_row(self, text):
        row = tk.Frame(self.main_container, bg="#120921")
        row.pack(fill="x", side="top", pady=2)

        # bullet pt
        bullet_btn = tk.Label(row, text="○", font=("Helvetica", 22), 
                              fg="#c37aff", bg="#120921", cursor="hand2",
                              width=3, pady=5) 
        bullet_btn.pack(side="left", padx=(5, 15)) 

        task_edit = tk.Entry(row, font=self.font_normal, bg="#120921", fg="#c37aff", 
                             bd=0, insertbackground="white", highlightthickness=1, 
                             highlightbackground="#120921")
        task_edit.insert(0, text)
        task_edit.pack(side="left", fill="x", expand=True, padx=(5, 15))

        # Strike through
        bullet_btn.bind("<Button-1>", lambda e: self.toggle_strike(task_edit, bullet_btn))

        # Right-click to Delete
        for btn in ["<Button-2>", "<Button-3>"]:
            row.bind(btn, lambda e: row.destroy())
            bullet_btn.bind(btn, lambda e: row.destroy())
            task_edit.bind(btn, lambda e: row.destroy())

        # Hover
        task_edit.bind("<Enter>", lambda e: task_edit.config(highlightbackground="#3d2b56"))
        task_edit.bind("<Leave>", lambda e: task_edit.config(highlightbackground="#120921"))
        task_edit.bind("<FocusOut>", lambda e: self.on_edit_finish(task_edit))
        
    def toggle_strike(self, entry_widget, circle_widget):
        current_font = entry_widget.cget("font")
        if "overstrike" in str(current_font):
            entry_widget.config(font=self.font_normal, fg="#c37aff")
            circle_widget.config(text="○", fg="#c37aff")
        else:
            entry_widget.config(font=self.font_done, fg="#2d1b4d")
            circle_widget.config(text="●", fg="#2d1b4d")

    def on_edit_finish(self, widget):
        if not widget.get().strip():
            widget.master.destroy()
