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

    def on_close(self):
        print("Saving tasks...") #TO DEBUG
        self.save_tasks()
        self.window.destroy()
        
    def setup_input_line(self):
        # Pack to main_container so it stays relative to the tasks
        self.input_frame = tk.Frame(self.main_container, bg="#120921")
        # self.input_frame.pack(fill="x", side="top", pady=5) #<-- USE IF WANT TASKS TO POPULATE AT THE TOP
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

        # Make row draggable
        row.bind("<Button-1>", lambda e, r=row: self.start_drag(e, r))
        row.bind("<B1-Motion>", lambda e, r=row: self.on_drag(e, r))
        row.bind("<ButtonRelease-1>", lambda e, r=row: self.end_drag(e, r))
        # Change cursor to hand when hovering
        row.bind("<Enter>", lambda e, r=row: r.config(cursor="hand2"))
        row.bind("<Leave>", lambda e, r=row: r.config(cursor=""))
        
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

    def start_drag(self, event, row):
        """
        Begin drag: store row and create a placeholder.
        """
        self.drag_row = row
        # Get all task rows (excluding input frame)
        self.drag_rows = self.get_task_rows()
        self.drag_start_index = self.drag_rows.index(row)
        # Create a placeholder frame (darkened rectangle)
        self.placeholder = tk.Frame(self.main_container, bg="#4a4a6a", height=40)  # greyish rectangle
        self.placeholder.place_forget()
        # Store mouse offset
        self.drag_start_y = event.y_root
        # Bind global motion and release to main container
        self.main_container.bind("<B1-Motion>", self.on_drag_global)
        self.main_container.bind("<ButtonRelease-1>", self.end_drag_global)
        # Change cursor
        self.main_container.config(cursor="fleur")

    def on_drag_global(self, event):
        """
        Move placeholder to show where the dragged row will land.
        """
        if not hasattr(self, 'drag_row'):
            return
        # Get mouse y relative to main_container
        mouse_y = event.widget.winfo_pointery() - self.main_container.winfo_rooty()
        # Get all task rows EXCEPT dragging one
        rows = [r for r in self.drag_rows if r != self.drag_row]
        # Find target index
        target_index = 0
        for i, r in enumerate(rows):
            top = r.winfo_y()
            bottom = top + r.winfo_height()
            if mouse_y < top:
                target_index = i
                break
            elif top <= mouse_y <= bottom:
                mid = (top + bottom) / 2
                target_index = i if mouse_y < mid else i+1
                break
            else:
                target_index = i+1
        else: # If mouse below all rows
            target_index = len(rows)
        self.show_placeholder_at_index(target_index)

    def show_placeholder_at_index(self, index):
        """
        Place a darkened rectangle at the insertion point.
        """
        if not hasattr(self, 'placeholder'):
            return
        rows = [r for r in self.drag_rows if r != self.drag_row]
        if not rows:
            y_pos = 5
        elif index == 0: # Before first row
            y_pos = rows[0].winfo_y() - 5
        elif index >= len(rows): # After last row
            y_pos = rows[-1].winfo_y() + rows[-1].winfo_height() + 5
        else: # Between rows
            prev_row = rows[index-1]
            y_pos = prev_row.winfo_y() + prev_row.winfo_height() + 5
        width = self.main_container.winfo_width() - 20
        self.placeholder.place(in_=self.main_container, x=10, y=y_pos, width=width, height=35)

    def end_drag_global(self, event):
        """
        Drop the dragged row at the placeholder position.
        """
        if not hasattr(self, 'drag_row'):
            self.cleanup_drag()
            return
        # Determine target index from placeholder position
        if hasattr(self, 'placeholder') and self.placeholder.winfo_ismapped():
            placeholder_y = self.placeholder.winfo_y()
            rows = [r for r in self.drag_rows if r != self.drag_row]
            target_index = 0
            for i, r in enumerate(rows):
                top = r.winfo_y()
                bottom = top + r.winfo_height()
                if placeholder_y < top:
                    break
                elif top <= placeholder_y <= bottom:
                    target_index = i
                    break
                else:
                    target_index = i+1
            # Reorder rows
            new_rows = self.drag_rows.copy()
            new_rows.remove(self.drag_row)
            new_rows.insert(target_index, self.drag_row)
            # Repack all rows in new order
            for r in new_rows:
                r.pack_forget()
                r.pack(fill="x", side="top", pady=2)
            # Ensure input frame is at bottom
            if self.input_frame is not None:
                self.input_frame.pack_forget()
                self.input_frame.pack(fill="x", side="top", pady=5)
            self.save_tasks()
        self.cleanup_drag()

    def cleanup_drag(self):
        """Remove drag state and placeholder."""
        if hasattr(self, 'drag_row'):
            del self.drag_row
        if hasattr(self, 'drag_rows'):
            del self.drag_rows
        if hasattr(self, 'drag_start_index'):
            del self.drag_start_index
        if hasattr(self, 'placeholder') and self.placeholder.winfo_exists():
            self.placeholder.destroy()
        self.main_container.unbind("<B1-Motion>")
        self.main_container.unbind("<ButtonRelease-1>")
        self.main_container.config(cursor="")
    
    def get_task_rows(self):
        """Return list of task rows (excluding input frame)."""
        rows = []
        for child in self.main_container.winfo_children():
            if isinstance(child, tk.Frame):
                if self.input_frame is not None and child == self.input_frame:
                    continue
                rows.append(child)
        return rows

    def get_task_rows(self):
        rows = []
        for child in self.main_container.winfo_children():
            if isinstance(child, tk.Frame):
                if self.input_frame is not None and child == self.input_frame:
                    continue
                rows.append(child)
        return rows
    
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

    def delete_row(self, row):
        row.destroy()
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
