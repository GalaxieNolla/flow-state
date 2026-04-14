import time
import subprocess
from pynput import mouse, keyboard
from AppKit import NSWorkspace
import Quartz.CoreGraphics as CG

BROWSER_APPS = ["Google Chrome", "Safari", "Firefox"]

class ActivityMonitor:
    def __init__(self):
        self.last_activity = time.time()
        self.mouse_listener = mouse.Listener(on_move=self.update_activity, on_click=self.update_activity)
        self.key_listener = keyboard.Listener(on_press=self.update_activity)
        self.mouse_listener.start()
        self.key_listener.start()

    def update_activity(self, *args):
        self.last_activity = time.time()

    def get_idle_time(self):
        return time.time() - self.last_activity

    def get_browser_title(self, app_name):
        scripts = {
            "Google Chrome": 'tell application "Google Chrome" to return title of active tab of front window',
            "Safari": 'tell application "Safari" to return name of current tab of front window',
            "Firefox": 'tell application "Firefox" to return title of front window',
        }
        script = scripts.get(app_name)
        if not script:
            return ""
        try:
            result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True, timeout=1)
            return result.stdout.strip()
        except:
            return ""

    def get_active_info(self):
        try:
            workspace = NSWorkspace.sharedWorkspace()
            app_name = workspace.frontmostApplication().localizedName()
            
            if app_name in BROWSER_APPS:
                title = self.get_browser_title(app_name)
                print(f"Browser title: '{title}'")
                return app_name, title

            options = CG.kCGWindowListOptionOnScreenOnly | CG.kCGWindowListExcludeDesktopElements
            window_list = CG.CGWindowListCopyWindowInfo(options, CG.kCGNullWindowID)

            if not window_list:
                return app_name, ""

            for window in window_list:
                owner = window.get('kCGWindowOwnerName', '')
                title = window.get('kCGWindowName', '')
                if owner == app_name and title and title.strip():
                    return app_name, title

            return app_name, ""
        except Exception as e:
            print(f"Monitor Error: {e}")
            return "Error", str(e)
