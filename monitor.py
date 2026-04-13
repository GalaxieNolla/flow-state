import time
from pynput import mouse, keyboard
from AppKit import NSWorkspace

class ActivityMonitor:
    def __init__(self):
        self.last_activity = time.time()
        
        # Background listeners
        self.mouse_listener = mouse.Listener(on_move=self.update_activity, on_click=self.update_activity)
        self.key_listener = keyboard.Listener(on_press=self.update_activity)
        self.mouse_listener.start()
        self.key_listener.start()

    def update_activity(self, *args):
        self.last_activity = time.time()

    def get_idle_time(self):
        return time.time() - self.last_activity

    def get_active_app(self):
        try:
            active_app = NSWorkspace.sharedWorkspace().frontmostApplication()
            if active_app:
                return active_app.localizedName()
            return "Unknown"
        except:
            return "Searching..."
