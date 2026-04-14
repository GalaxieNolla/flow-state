import tkinter as tk

class TaskSticky:
    def __init__(self, root):
        self.root = root
        self.window = None
        self.font_normal = ("Helvetica", 18)
        self.font_done = ("Helvetica", 18, "overstrike") #for strikethrough

    def open(self):
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return

        self.window = tk.Toplevel(self.root)
        self.window.title("Tasks")
        self.window.geometry("350x500")
        self.window.configure(bg="#120921")
        self.window.attributes("-topmost", True)

        # Main container for the list
        self.scroll_canvas = tk.Canvas(self.window, bg="#120921", highlightthickness=0)
        self.task_list_frame = tk.Frame(self.scroll_canvas, bg="#120921")
        self.scroll_canvas.pack(fill="both", expand=True, padx=15, pady=10)
        self.scroll_canvas.create_window((0,0), window=self.task_list_frame, anchor="nw")

        # '+'
        self.setup_input_line()

    def setup_input_line(self):
        self.input_frame = tk.Frame(self.task_list_frame, bg="#120921")
        self.input_frame.pack(fill="x", side="top") # Growing downwards

        plus_label = tk.Label(self.input_frame, text="+", font=self.font_normal, fg="#c37aff", bg="#120921")
        plus_label.pack(side="left", padx=(0, 10))

        self.new_entry = tk.Entry(self.input_frame, font=self.font_normal, bg="#120921", 
                                  fg="white", bd=0, insertbackground="white")
        self.new_entry.pack(side="left", fill="x", expand=True)
        self.new_entry.focus_set()
        
        # Press Enter to add task and move the "+" down
        self.new_entry.bind("<Return>", lambda e: self.commit_task())

    def commit_task(self):
        text = self.new_entry.get().strip()
        if not text:
            return

        self.input_frame.destroy()
        self.create_task_row(text)
        self.setup_input_line()

    def create_task_row(self, text):
        row = tk.Frame(self.task_list_frame, bg="#120921")
        row.pack(fill="x", side="top", pady=2)

        # user can edit entries
        task_edit = tk.Entry(row, font=self.font_normal, bg="#120921", fg="white", 
                             bd=0, insertbackground="white")
        task_edit.insert(0, text)
        task_edit.pack(side="left", fill="x", expand=True)

        # strikethrough completed tasks
        task_edit.bind("<Shift-Button-1>", lambda e: self.toggle_strike(task_edit))
        
        task_edit.bind("<FocusOut>", lambda e: self.on_edit_finish(task_edit))

    def toggle_strike(self, widget):
        current_font = widget.cget("font")
        if "overstrike" in str(current_font):
            widget.config(font=self.font_normal, fg="white")
        else:
            widget.config(font=self.font_done, fg="#7a7a7a")

    def on_edit_finish(self, widget):
        if not widget.get().strip():
            widget.master.destroy()
