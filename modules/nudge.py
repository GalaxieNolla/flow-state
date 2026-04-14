import time
import threading
from Foundation import NSObject, NSTimer
import AppKit
from AppKit import (
    NSWindow, NSWindowStyleMaskBorderless, NSBackingStoreBuffered,
    NSColor, NSTextField, NSFont, NSMakeRect, NSFloatingWindowLevel,
    NSWindowCollectionBehaviorCanJoinAllSpaces,
    NSWindowCollectionBehaviorStationary,
    NSNonactivatingPanelMask, NSPanel
)

class Nudge:
    def __init__(self, root):
        self.root = root
        self.window = None
        self.streak_start = time.time()
        self.streak_minutes = 0
        self.countdown = 0
        self.countdown_job = None
        self.is_distracted = False
        #ensures nudgei snot blippy
        self._last_shown = 0
        self._COOLDOWN = 3.0

    def show(self, site_name=""):
        self.is_distracted = True
    
        if self.window is not None:
            self._update_labels(site_name)
            return
    
        now = time.time()
        if now - self._last_shown < self._COOLDOWN:
            return
        self._last_shown = now
    
        if self.countdown == 0:
            self.countdown = 30
    
        self.root.after(0, lambda: self._create_window(site_name))

    def _create_window(self, site_name):
        screen = AppKit.NSScreen.mainScreen()
        sw = screen.frame().size.width
        sh = screen.frame().size.height
        x = sw - 260
        y = sh - 140
    
        self.window = NSPanel.alloc().initWithContentRect_styleMask_backing_defer_(
            NSMakeRect(x, y, 240, 120),
            NSNonactivatingPanelMask | NSWindowStyleMaskBorderless,
            NSBackingStoreBuffered,
            False
        )
        self.window.setLevel_(NSFloatingWindowLevel)
        self.window.setOpaque_(False)
        self.window.setAlphaValue_(0.93)
        self.window.setBackgroundColor_(
            NSColor.colorWithRed_green_blue_alpha_(0.071, 0.035, 0.129, 1.0)
        )
        self.window.setCollectionBehavior_(
            NSWindowCollectionBehaviorCanJoinAllSpaces |
            NSWindowCollectionBehaviorStationary
        )
        self.window.makeKeyAndOrderFront_(None)
        self.window.resignKeyWindow()
    
        cv = self.window.contentView()
        self._add_label(cv, "🔥", 14, 86, 30, 30, size=20, color=(1,1,1))
        self.streak_label = self._add_label(cv, self._streak_text(), 48, 88, 180, 20, size=11, color=(0.765, 0.478, 1.0))
        self.msg_label = self._add_label(cv, f"hey, {site_name} isn't it...", 14, 58, 212, 28, size=10, color=(1.0, 0.42, 0.42), italic=True)
        self.timer_label = self._add_label(cv, f"{self.countdown}s to get back", 14, 14, 212, 20, size=10, color=(0.478, 0.416, 0.604))
    
        self._tick()

    def _add_label(self, parent, text, x, y, w, h, size=12, color=(1,1,1), italic=False):
        field = NSTextField.alloc().initWithFrame_(NSMakeRect(x, y, w, h))
        field.setStringValue_(text)
        field.setBezeled_(False)
        field.setDrawsBackground_(False)
        field.setEditable_(False)
        field.setSelectable_(False)
        field.setFont_(NSFont.italicSystemFontOfSize_(size) if italic else NSFont.systemFontOfSize_(size))
        field.setTextColor_(NSColor.colorWithRed_green_blue_alpha_(*color, 1.0))
        parent.addSubview_(field)
        return field
    
    def hide(self):
        self.is_distracted = False
        self.countdown = 0
        if self.countdown_job:
            self.root.after_cancel(self.countdown_job)
            self.countdown_job = None
        if self.window is not None:
            self.window.orderOut_(None)
            self.window = None
        self.streak_start = time.time()

    def reset_streak(self):
        self.streak_start = time.time()
        self.streak_minutes = 0

    def _streak_text(self):
        mins = int((time.time() - self.streak_start) / 60)
        return f"{mins} min focus streak"

    def _update_labels(self, site_name=""):
        if self.window and hasattr(self, 'streak_label'):
            self.streak_label.config(text=self._streak_text())
        if site_name and self.window and hasattr(self, 'msg_label'):
            self.msg_label.config(text=f"hey, {site_name} isn't it...")

    def _tick(self):
        if self.window is None:
            return
        self.countdown -= 1
        if self.countdown <= 0:
            if hasattr(self, 'timer_label'):
                self.timer_label.config(text="streak reset!", fg="#ff4b4b")
            self.reset_streak()
            self.countdown_job = self.root.after(2000, self._close_after_reset)
        else:
            if hasattr(self, 'timer_label'):
                self.timer_label.config(text=f"{self.countdown}s to get back")
            self.countdown_job = self.root.after(1000, self._tick)

    def _close_after_reset(self):
        if self.window is not None:
            self.window.orderOut_(None)
            self.window = None
