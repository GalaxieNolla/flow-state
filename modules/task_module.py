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
        self.window.bind("<Button-3>", lambda e: "break")
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
        # Change cursor when hover
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
        row.task_edit = task_edit
        task_edit.insert(0, text)
        task_edit.pack(side="left", fill="x", expand=True, padx=(0, 10))
        task_edit.row = row  # link back
        task_edit.bind("<Button-1>", lambda e, r=row: self.start_drag(e, r))
    
        # Priority selector (right side) - a label that looks like a button with triangle
        priority_btn = tk.Label(row, text=f"▼ {priority}", font=("Cinzel", 9, "bold"), #OR NONE DEBUG
                                fg="#a78bfa", bg=self.priority_colors[priority]["bg"],
                                cursor="hand2", padx=5)
        priority_btn.pack(side="right", padx=(0, 10))
        priority_btn.current = priority
        priority_btn.row = row
    
        # Bind click to cycle priority
        priority_btn.bind("<Button-1>", lambda e, r=row, btn=priority_btn: self.cycle_priority(r, btn))
    
        # Strikethrough toggle (left bullet)
        bullet_btn.bind("<Button-1>", lambda e: self.toggle_strike(task_edit, bullet_btn, row))
    
        # Right-click to delete row
        for widget in (row, bullet_btn, task_edit, priority_btn):
            widget.bind("<Button-3>", lambda e, r=row: self.delete_row(r) or "break")
    
        # Hover
        task_edit.bind("<Enter>", lambda e: task_edit.config(highlightbackground="#3d2b56"))
        task_edit.bind("<Leave>", lambda e: task_edit.config(highlightbackground="#120921"))
    
        # Save task text on focus out
        task_edit.bind("<FocusOut>", lambda e: self.on_edit_finish(task_edit))
    
        if done:
            self.toggle_strike(task_edit, bullet_btn, row)  # apply strikethrough if loaded as done

        '''# Ensure input frame stays at bottom DEBUG
        if self.input_frame is not None:
            self.input_frame.pack_forget()
            self.input_frame.pack(fill="x", side="bottom", pady=5)'''

    def start_drag(self, event, row):
        self.drag_row = row
        self.drag_start_y = event.y_root
        self.drag_dragging = False
    
        # Placeholder for possible row position
        self.drag_placeholder = tk.Frame(
            self.main_container,
            bg="#2a1060",
            height=row.winfo_height() or 40
        )
    
        # Ghost / shadow row
        text = row.task_edit.get() if hasattr(row, 'task_edit') else ""
        self.drag_ghost = tk.Toplevel(self.window)
        self.drag_ghost.overrideredirect(True)
        self.drag_ghost.attributes("-alpha", 0.75)
        self.drag_ghost.attributes("-topmost", True)
        ghost_label = tk.Label(
            self.drag_ghost,
            text=text,
            font=self.font_normal,
            fg=self.priority_colors[row.priority]["entry_fg"],
            bg=self.priority_colors[row.priority]["bg"],
            padx=15, pady=8
        )
        ghost_label.pack()
        # Position ghost at current mouse location
        self._move_ghost(event.x_root, event.y_root)
    
        self.window.bind("<B1-Motion>", self.on_drag_global)
        self.window.bind("<ButtonRelease-1>", self.end_drag_global)
        return "break"

    def _move_ghost(self, x_root, y_root):
        if hasattr(self, 'drag_ghost') and self.drag_ghost.winfo_exists():
            self.drag_ghost.geometry(f"+{x_root + 10}+{y_root - 15}")

    def on_drag_global(self, event):
        if not hasattr(self, 'drag_row'):
            return
    
        self.drag_dragging = True
        self._move_ghost(event.x_root, event.y_root)
    
        rows = self.get_task_rows()
        if self.drag_row not in rows:
            return
    
        drag_idx = rows.index(self.drag_row)
    
        # Hide the real row while dragging; show placeholder in its place
        self.drag_row.pack_forget()
    
        # Find where to insert placeholder based on mouse y relative to container
        container_y = event.y_root - self.main_container.winfo_rooty()
        insert_idx = drag_idx  # default: stay in place
    
        for i, r in enumerate(rows):
            if r is self.drag_row:
                continue
            row_top = r.winfo_y()
            row_mid = row_top + r.winfo_height() // 2
            if container_y < row_mid:
                insert_idx = i
                break
            else:
                insert_idx = i + 1
    
        # Repack: insert placeholder at insert_idx among the other rows
        other_rows = [r for r in rows if r is not self.drag_row]
        self.drag_placeholder.pack_forget()
    
        for i, r in enumerate(other_rows):
            r.pack_forget()
    
        for i, r in enumerate(other_rows):
            if i == insert_idx:
                self.drag_placeholder.pack(fill="x", side="top", pady=2)
            r.pack(fill="x", side="top", pady=2)
    
        # If inserting at the end
        if insert_idx >= len(other_rows):
            self.drag_placeholder.pack(fill="x", side="top", pady=2)
    
        self.drag_insert_idx = insert_idx
    
        # Keep input frame at bottom
        if self.input_frame:
            self.input_frame.pack_forget()
            self.input_frame.pack(fill="x", side="top", pady=5)
    
        return "break"

    def end_drag_global(self, event):
        if not hasattr(self, 'drag_row'):
            return
    
        rows = self.get_task_rows()
        drag_idx = rows.index(self.drag_row) if self.drag_row in rows else 0
        insert_idx = getattr(self, 'drag_insert_idx', drag_idx)
    
        # Remove placeholder, re-insert drag_row at correct position
        self.drag_placeholder.pack_forget()
        other_rows = [r for r in rows if r is not self.drag_row]
    
        for r in other_rows:
            r.pack_forget()
    
        for i, r in enumerate(other_rows):
            if i == insert_idx:
                self.drag_row.pack(fill="x", side="top", pady=2)
            r.pack(fill="x", side="top", pady=2)
    
        if insert_idx >= len(other_rows):
            self.drag_row.pack(fill="x", side="top", pady=2)
    
        # Destroy ghost
        if hasattr(self, 'drag_ghost') and self.drag_ghost.winfo_exists():
            self.drag_ghost.destroy()
    
        if self.input_frame:
            self.input_frame.pack_forget()
            self.input_frame.pack(fill="x", side="top", pady=5)
    
        self.cleanup_drag()
        self.save_tasks()
        return "break"

    def cleanup_drag(self):
        for attr in ('drag_row', 'drag_start_y', 'drag_dragging',
                     'drag_insert_idx', 'drag_placeholder', 'drag_ghost', 'drag_rows'):
            if hasattr(self, attr):
                delattr(self, attr)
        self.window.unbind("<B1-Motion>")
        self.window.unbind("<ButtonRelease-1>")
    
    def get_task_rows(self):
        """
        Return list of task rows (excluding input frame).
        """
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
        # Check if task is currently strikethrough
        is_striked = "overstrike" in str(row.task_edit.cget("font")) if hasattr(row, 'task_edit') else False
        btn.config(text=f"▼ {new_priority}")

        # Update colors of row and widgets
        colors = self.priority_colors[new_priority]
        row.config(bg=colors["bg"])
        
        # If task is strikethrough, use greyed colors
        if is_striked:
            text_color = self.darken_color(colors["entry_fg"], 0.4)
            bullet_color = self.darken_color(colors["bullet"], 0.4)
        else:
            text_color = colors["entry_fg"]
            bullet_color = colors["bullet"]
        
        for child in row.winfo_children():
            if isinstance(child, tk.Label):
                if child.cget("text") in ("○", "●"):
                    child.config(fg=bullet_color, bg=colors["bg"])
                else:  # priority button
                    child.config(bg=colors["bg"])
            elif isinstance(child, tk.Entry):
                child.config(bg=colors["bg"], fg=text_color)
        
        btn.config(bg=colors["bg"])
        self.save_tasks()

    def darken_color(self, hex_color, factor=0.3):
        """
        Return desaturated/darkened version for completed tasks.
        """
        hex_color = hex_color.lstrip('#')
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        # Grayscale intensity
        grey = int(r * 0.299 + g * 0.587 + b * 0.114)
        # paint mixing <3
        r = int(r * factor + grey * (1 - factor))
        g = int(g * factor + grey * (1 - factor))
        b = int(b * factor + grey * (1 - factor))
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def delete_row(self, row):
        row.destroy()
        self.save_tasks()
        return "break"
    
    def toggle_strike(self, entry_widget, circle_widget, row):
        """
        Toggle strikethrough on a task. When striked, text and bullet become a
        darker/greyer version of the priority's original color.
        """
        current_font = entry_widget.cget("font")
        priority = getattr(row, "priority", "None")
        original_fg = self.priority_colors[priority]["entry_fg"]
        original_bullet = self.priority_colors[priority]["bullet"]
        grey_color = self.darken_color(original_fg, 0.4)
        
        if "overstrike" in str(current_font): # Remove strikethrough: revert to original colors
            entry_widget.config(font=self.font_normal, fg=original_fg)
            circle_widget.config(text="○", fg=original_bullet)
        else: # Apply strikethrough: use darkened colors
            entry_widget.config(font=self.font_done, fg=grey_color)
            circle_widget.config(text="●", fg=grey_color)

    def on_edit_finish(self, widget):
        if not widget.get().strip():
            widget.master.destroy()
