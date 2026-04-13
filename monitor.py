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

    """def get_active_info(self):
        try:
            workspace = NSWorkspace.sharedWorkspace()
            active_app = workspace.frontmostApplication()

            # Safety check if app is unknown
            if not active_app:
                return "Finder", "" # Default to Finder if it's confused
            
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
            return "Finder", "" """

def get_active_info(self):
        try:
            workspace = NSWorkspace.sharedWorkspace()
            
            # activeApplication() instead of frontmostApplication() 4 reliability?
            active_info = workspace.activeApplication()
            app_name = active_info.get('NSApplicationName', 'Unknown')
            pid = active_info.get('NSApplicationProcessIdentifier')

            # Window Title Check
            from Quartz import CGWindowListCopyWindowInfo, kCGWindowListOptionOnScreenOnly, kCGExcludeDesktopElements
            window_list = CGWindowListCopyWindowInfo(kCGWindowListOptionOnScreenOnly | kCGExcludeDesktopElements, 0)
            
            window_title = ""
            if window_list and pid:
                for window in window_list:
                    if window.get('kCGWindowOwnerPID') == pid:
                        window_title = window.get('kCGWindowName', '')
                        if window_title:
                            break
            
            return app_name, window_title
        except Exception as e:
            return "Unknown", ""
