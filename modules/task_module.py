import tkinter as tk
import json
import os

saved_sticky = os.path.join(os.path.dirname(__file__), "tasks.json")

class TaskSticky:
    def __init__(self, root):
        self.root = root
        self.window = None
        self.input_frame = None
        self.font_normal = ("Cinzel", 18)
        self.font_done = ("Cinzel", 18, "overstrike") # for strikethrough
        self.instruction_font = ("Cinzel", 10, "italic") # for instructions :3

        # priority sorting
        self.priority_levels = ["None", "Low", "Medium", "High"]
        self.priority_colors = {
            "None": {"bullet": "#c37aff", "bg": "#120921", "entry_fg": "#c37aff"},
            "Low": {"bullet": "#6a9fb5", "bg": "#1a2a36", "entry_fg": "#aaccdd"},
            "Medium": {"bullet": "#e5b567", "bg": "#2a2416", "entry_fg": "#f5d98f"},
            "High": {"bullet": "#e35f5f", "bg": "#2e1a1a", "entry_fg": "#ffaaaa"},
            "LongTerm": {"bullet": "#b381d3", "bg": "#2a1f33", "entry_fg": "#dcb5ff"},  # extra
        }

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
        text="[Delete: Right-click task • Complete: Left-click bullet]",
        font=("Georgia", 10, "italic"),
        fg="#6b4c8a",
        bg="#120921",
        pady=5
        )
        self.instruction_label.pack(side="bottom", fill="x")

    def save_tasks(self):
        tasks = []
        for row in self.main_container.winfo_children():
            if (self.input_frame is not None and row == self.input_frame) or not isinstance(row, tk.Frame):
                continue
            # find the Entry widget in the row
            for widget in row.winfo_children():
                if isinstance(widget, tk.Entry):
                    text = widget.get().strip()
                    done = "overstrike" in str(widget.cget("font"))
                    priority = getattr(row, "priority", "None")
                    if text:
                        tasks.append({"text": text, "done": done, "priority": priority})
        with open(saved_sticky, "w") as f:
            json.dump(tasks, f)

    def load_tasks(self):
        if not os.path.exists(saved_sticky):
            return
        with open(saved_sticky, "r") as f:
            tasks = json.load(f)
        for task in tasks:
            self.create_task_row(task["text"], done=task.get("done", False), priority=task.get("priority", "None"))
        self.sort_tasks()

    def on_close(self):
        print("Saving tasks...") #TO DEBUG
        self.save_tasks()
        self.window.destroy()
        
    def setup_input_line(self):
        # Pack to main_container so it stays relative to the tasks
        self.input_frame = tk.Frame(self.main_container, bg="#120921")
        # self.input_frame.pack(fill="x", side="top", pady=5) #<-- USE IF WANT TASKS TO POPULATE AT THE TOP
        self.input_frame.pack(fill="x", side="bottom", pady=5)

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

    '''def create_task_row(self, text, done=False):
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
        task_edit.bind("<FocusOut>", lambda e: self.on_edit_finish(task_edit))'''

    def create_task_row(self, text, done=False, priority="None"):
        row = tk.Frame(self.main_container, bg=self.priority_colors[priority]["bg"])
        row.pack(fill="x", side="top", pady=2)
        row.priority = priority  # store on row widget
        row.task_text = text
    
        # Bullet (left)
        bullet_btn = tk.Label(row, text="○", font=("Cinzel", 22),
                              fg=self.priority_colors[priority]["bullet"], bg=self.priority_colors[priority]["bg"],
                              cursor="hand2", padx=5, pady=5)
        bullet_btn.pack(side="left", padx=(5, 10))
    
        # Entry (middle)
        task_edit = tk.Entry(row, font=self.font_normal, bg=self.priority_colors[priority]["bg"],
                             fg=self.priority_colors[priority]["entry_fg"], bd=0,
                             insertbackground="white", highlightthickness=1,
                             highlightbackground="#a78bfa")
        task_edit.insert(0, text)
        task_edit.pack(side="left", fill="x", expand=True, padx=(0, 10))
        task_edit.row = row  # link back
    
        # Priority selector (right side) - a label that looks like a button with triangle
        priority_btn = tk.Label(row, text="▼ None", font=("Cinzel", 9, "bold"),
                                fg="#a78bfa", bg=self.priority_colors[priority]["bg"],
                                cursor="hand2", padx=5)
        priority_btn.pack(side="right", padx=(0, 10))
        priority_btn.current = priority
        priority_btn.row = row
    
        # Bind click to cycle priority
        priority_btn.bind("<Button-1>", lambda e, r=row, btn=priority_btn: self.cycle_priority(r, btn))
    
        # Strikethrough toggle (left bullet)
        bullet_btn.bind("<Button-1>", lambda e: self.toggle_strike(task_edit, bullet_btn))
    
        # Right-click to delete row
        for widget in (row, bullet_btn, task_edit, priority_btn):
            widget.bind("<Button-3>", lambda e, r=row: self.delete_row(r))
    
        # Hover
        task_edit.bind("<Enter>", lambda e: task_edit.config(highlightbackground="#3d2b56"))
        task_edit.bind("<Leave>", lambda e: task_edit.config(highlightbackground="#120921"))
    
        # Save task text on focus out
        task_edit.bind("<FocusOut>", lambda e: self.on_edit_finish(task_edit))
    
        if done:
            self.toggle_strike(task_edit, bullet_btn)  # apply strikethrough if loaded as done

        '''# Ensure input frame stays at bottom DEBUG
        if self.input_frame is not None:
            self.input_frame.pack_forget()
            self.input_frame.pack(fill="x", side="bottom", pady=5)'''

    def cycle_priority(self, row, btn):
        """
        Cycle priority: None -> Low -> Medium -> High -> None
        """
        current = row.priority
        levels = self.priority_levels
        next_idx = (levels.index(current) + 1) % len(levels)
        new_priority = levels[next_idx]
        row.priority = new_priority
        btn.config(text=f"▼ {new_priority}")
        
        # Update colors of row and widgets
        colors = self.priority_colors[new_priority]
        row.config(bg=colors["bg"])
        
        for child in row.winfo_children():
            if isinstance(child, tk.Label):
                if "text" in str(child.cget("text")) and child != btn:  # bullet label
                    child.config(fg=colors["bullet"], bg=colors["bg"])
                else:  # priority button itself
                    child.config(bg=colors["bg"])
            elif isinstance(child, tk.Entry):
                child.config(bg=colors["bg"], fg=colors["entry_fg"])
        
        btn.config(bg=colors["bg"])
        self.save_tasks()
        self.sort_tasks()  # reorder rows based on priority

    def delete_row(self, row):
        row.destroy()
        self.save_tasks()
    
    def sort_tasks(self):
        """
        Re-sort all task rows by priority: High > Medium > Low > None
        """
        rows = []
        for child in self.main_container.winfo_children():
            if isinstance(child, tk.Frame):
                if self.input_frame is not None and child == self.input_frame:
                    continue
                rows.append(child)
        
        # Define sort key
        priority_order = {"High": 0, "Medium": 1, "Low": 2, "None": 3}
        rows.sort(key=lambda r: priority_order.get(getattr(r, "priority", "None"), 3))

        for row in rows:
            row.pack_forget()
            row.pack(fill="x", side="top", pady=2)
        # Re-pack input frame at the bottom if it exists
        if self.input_frame is not None:
            self.input_frame.pack_forget()
            #self.input_frame.pack(fill="x", side="top", pady=5) # KEEP IF WANT TASKS TO POPULATE AT TOP
            self.input_frame.pack(fill="x", side="bottom", pady=5)
            
        self.save_tasks()
    
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
