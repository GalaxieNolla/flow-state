import tkinter as tk
import json
import os

saved_sticky = os.path.join(os.path.dirname(__file__), "tasks.json")

class TaskSticky:
    def __init__(self, root):
        self.root = root
        self.window = None
        self.font_normal = ("Cinzel", 18)
        self.font_done = ("Cinzel", 18, "overstrike") # for strikethrough
        self.instruction_font = ("Cinzel", 10, "italic") # for instructions :3

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

        # Load when open
        self.load_tasks()
        self.setup_input_line()
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)  # save when closed

        # give user the instructions for to-do list
        self.instruction_label = tk.Label(
        self.window, 
        text="Delete: Right-click task • Complete: Left-click bullet",
        font=("Ariel", 10, "bold"),
        fg="#6b4c8a",
        bg="#120921",
        pady=5
        )
        self.instruction_label.pack(side="bottom", fill="x")

    def save_tasks(self):
        tasks = []
        for row in self.main_container.winfo_children():
            if row == self.input_frame:
                continue
            # find the Entry widget in the row
            for widget in row.winfo_children():
                if isinstance(widget, tk.Entry):
                    text = widget.get().strip()
                    done = "overstrike" in str(widget.cget("font"))
                    if text:
                        tasks.append({"text": text, "done": done})
        with open(saved_sticky, "w") as f:
            json.dump(tasks, f)

    def load_tasks(self):
        if not os.path.exists(saved_sticky):
            return
        with open(saved_sticky, "r") as f:
            tasks = json.load(f)
        for task in tasks:
            self.create_task_row(task["text"], done=task.get("done", False))

    def on_close(self):
        print("Saving tasks...") #TO DEBUG
        self.save_tasks()
        self.window.destroy()
        
    def setup_input_line(self):
        # Pack to main_container so it stays relative to the tasks
        self.input_frame = tk.Frame(self.main_container, bg="#120921")
        self.input_frame.pack(fill="x", side="top", pady=5)

        plus_label = tk.Label(self.input_frame, text=" +", font=self.font_normal, fg="#c37aff", bg="#120921")
        plus_label.pack(side="left", padx=(5, 10))

        self.new_entry = tk.Entry(self.input_frame, font=self.font_normal, bg="#120921", 
                                  fg="#c37aff", bd=0, insertbackground="white",
                                  highlightthickness=1, highlightbackground="#c37aff", highlightcolor="#c37aff")
        self.new_entry.pack(side="left", fill="x", expand=True, padx=(0, 15))
        self.new_entry.focus_set()
        
        self.new_entry.bind("<Return>", lambda e: self.commit_task())

    def commit_task(self):
        text = self.new_entry.get().strip()
        if not text:
            return

        self.input_frame.destroy() # Remove old +
        self.create_task_row(text) # Add row to the container
        self.setup_input_line()    # New + dir under row

    def create_task_row(self, text, done=False):
        row = tk.Frame(self.main_container, bg="#120921")
        row.pack(fill="x", side="top", pady=2)

        # bullet pt
        bullet_btn = tk.Label(row, text="○", font=("Cinzel", 22), 
                              fg="#a78bfa", bg="#120921", cursor="hand2", #fg="#c37aff"
                              padx=5, pady=5) 
        bullet_btn.pack(side="left", padx=(5, 10)) 

        task_edit = tk.Entry(row, font=self.font_normal, bg="#120921", fg="#c37aff", 
                             bd=0, insertbackground="white", highlightthickness=1, 
                             highlightbackground="#a78bfa")
                             #highlightbackground="#120921")
        task_edit.insert(0, text)
        task_edit.pack(side="left", fill="x", expand=True, padx=(0, 15))

        if done:
            task_edit.config(font=self.font_done, fg="#2d1b4d")
            bullet_btn.config(text="●", fg="#2d1b4d")
        
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
