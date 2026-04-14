import time
from pynput import mouse, keyboard
from AppKit import NSWorkspace
import Quartz.CoreGraphics as CG

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
                options = CG.kCGWindowListOptionOnScreenOnly | CG.kCGWindowListExcludeDesktopElements
                window_list = CG.CGWindowListCopyWindowInfo(options, CG.kCGNullWindowID)
    
                if not window_list:
                    return app_name, "" # prev: "Unknown", ""
                
                for window in window_list:
                    if window.get('kCGWindowLayer', '') == app_name:
                        window_title = window.get('kCGWindowName', '')
                        if title and title.strip():
                            return app_name, title
                return app_name, ""
            except Exception as e:
                print(f"Monitor Error: {e}") #for debugging purposes
                return "Error", str(e)
