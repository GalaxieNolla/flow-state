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

    def get_active_info(self):
        try:
            workspace = NSWorkspace.sharedWorkspace()
            active_app = workspace.frontmostApplication()
            app_name = active_app.localizedName()
            
            # Grabs the specific title of the window from UI (e.g., "YouTube")
            from Quartz import CGWindowListCopyWindowInfo, kCGWindowListOptionOnScreenOnly, kCGExcludeDesktopElements
            window_list = CGWindowListCopyWindowInfo(kCGWindowListOptionOnScreenOnly | kCGExcludeDesktopElements, 0)
            
            window_title = ""
            for window in window_list:
                if window.get('kCGWindowOwnerPID') == active_app.processIdentifier():
                    window_title = window.get('kCGWindowName', '')
                    break
                    
            return app_name, window_title
        except:
            return "Unknown", ""
