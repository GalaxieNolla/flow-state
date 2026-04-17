import time
import subprocess
from pynput import mouse, keyboard
from AppKit import NSWorkspace
import Quartz.CoreGraphics as CG

BROWSER_APPS = ["Google Chrome", "Safari", "Firefox"]

class ActivityMonitor:
    def __init__(self):
        self.on_distraction = None
        self.last_activity = time.time()
        self.mouse_listener = mouse.Listener(on_move=self.update_activity, on_click=self.update_activity)
        self.key_listener = keyboard.Listener(on_press=self.update_activity)
        self.mouse_listener.start()
        self.key_listener.start()

    def update_activity(self, *args):
        self.last_activity = time.time()
        if self.on_distraction and self.is_distraction():
            self.on_distraction()

    def get_idle_time(self):
        return time.time() - self.last_activity

    def is_distraction(self):
        current_app, window_title = self.get_active_info()
        current_app = str(current_app).lower() # update both to be lowercase str, case sensitive
        window_title = str(window_title).lower()

        distraction_sites = ["youtube", "netflix", "twitter", "instagram", "tiktok", "ebay", "etsy", "reddit", "messages", "discord"]
        # Exceptions check -- berkeley, school, lecture, etc. or music
        exception = any(word in window_title.lower() for word in 
                        ["berkeley", "cal", "school", "lecture", "cs", "compsci", "polysci", "ds", "data science", "datasci", 
                         "classical", "music", "lofi", "instrumental", "spotify", "bcourses", "zoom", "pomodoro"])
        
        distraction = any(site in current_app for site in distraction_sites) or any(site in window_title for site in distraction_sites)
        is_exception = any(word in window_title for word in exception_keywords)
        return is_distracting and not is_exception

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
                # print(f"Browser title: '{title}'") for debugging
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
