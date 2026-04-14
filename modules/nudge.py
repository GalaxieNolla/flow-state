import time
import objc
import AppKit
from AppKit import (
    NSWindowStyleMaskBorderless, NSBackingStoreBuffered,
    NSColor, NSTextField, NSFont, NSMakeRect, NSFloatingWindowLevel,
    NSWindowCollectionBehaviorCanJoinAllSpaces,
    NSWindowCollectionBehaviorStationary,
    NSNonactivatingPanelMask, NSPanel, NSView, NSBezierPath
)
 
 
class ProgressBar(NSView):
    def init(self):
        self = objc.super(ProgressBar, self).init()
        if self is None:
            return None
        self._progress = 1.0
        self._color = NSColor.colorWithRed_green_blue_alpha_(0.53, 0.35, 0.85, 1.0)
        return self
 
    def setProgress_(self, value):
        self._progress = max(0.0, min(1.0, value))
        self.setNeedsDisplay_(True)
 
    def drawRect_(self, rect):
        # dark track
        NSColor.colorWithRed_green_blue_alpha_(0.2, 0.15, 0.3, 1.0).setFill()
        track = NSBezierPath.bezierPathWithRoundedRect_xRadius_yRadius_(rect, 3, 3)
        track.fill()
        # filled portion
        filled = NSMakeRect(
            rect.origin.x, rect.origin.y,
            rect.size.width * self._progress, rect.size.height
        )
        self._color.setFill()
        bar = NSBezierPath.bezierPathWithRoundedRect_xRadius_yRadius_(filled, 3, 3)
        bar.fill()
 
 
class Nudge:
    COUNTDOWN_SECS = 30
 
    def __init__(self, root):
        self.root = root
        self.window = None
        self.streak_start = time.time()
        self.countdown = 0
        self.countdown_job = None
        self.is_distracted = False
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
            self.countdown = self.COUNTDOWN_SECS
        self.root.after(0, lambda: self._create_window(site_name))
 
    def hide(self):
        self.is_distracted = False
        self.countdown = 0
        if self.countdown_job:
            self.root.after_cancel(self.countdown_job)
            self.countdown_job = None
        if self.window is not None:
            self.window.orderOut_(None)
            self.window = None
        # don't reset streak here — only reset on full timeout
 
    def reset_streak(self):
        self.streak_start = time.time()
 
    def _create_window(self, site_name):
        screen = AppKit.NSScreen.mainScreen()
        sw = screen.frame().size.width
        sh = screen.frame().size.height
        W, H = 240, 130
        x = sw - W - 20
        y = sh - H - 20
 
        self.window = NSPanel.alloc().initWithContentRect_styleMask_backing_defer_(
            NSMakeRect(x, y, W, H),
            NSNonactivatingPanelMask | NSWindowStyleMaskBorderless,
            NSBackingStoreBuffered,
            False
        )
        self.window.setLevel_(NSFloatingWindowLevel)
        self.window.setOpaque_(False)
        self.window.setAlphaValue_(0.95)
        self.window.setBackgroundColor_(
            NSColor.colorWithRed_green_blue_alpha_(0.071, 0.035, 0.129, 1.0)
        )
        self.window.setCollectionBehavior_(
            NSWindowCollectionBehaviorCanJoinAllSpaces |
            NSWindowCollectionBehaviorStationary
        )
 
        cv = self.window.contentView()
        cv.setWantsLayer_(True)
        cv.layer().setCornerRadius_(12)
        cv.layer().setMasksToBounds_(True)
 
        self.window.makeKeyAndOrderFront_(None)
        self.window.resignKeyWindow()
 
        # streak
        self._add_label(cv, "🔥", 14, H - 34, 28, 24, size=18)
        self.streak_label = self._add_label(
            cv, self._streak_text(), 44, H - 32, 180, 20,
            size=11, color=(0.765, 0.478, 1.0)
        )
 
        # italic distraction message
        self.msg_label = self._add_label(
            cv, f"hey, {site_name} isn't it...", 14, H - 60, W - 28, 20,
            size=10, color=(1.0, 0.42, 0.42), italic=True
        )
 
        # progress bar
        self.progress_bar = ProgressBar.alloc().init()
        self.progress_bar.setFrame_(NSMakeRect(14, H - 82, W - 28, 6))
        cv.addSubview_(self.progress_bar)
 
        # countdown label (right-aligned)
        self.timer_label = self._add_label(
            cv, f"{self.countdown}s to get back", W - 120, H - 100, 106, 18,
            size=9, color=(0.478, 0.416, 0.604)
        )
 
        # "distracted" badge bottom-left
        self.badge_label = self._add_label(
            cv, "  distracted  ", 14, 10, 90, 22,
            size=10, color=(0.9, 0.5, 0.2)
        )
        self.badge_label.setDrawsBackground_(True)
        self.badge_label.setBackgroundColor_(
            NSColor.colorWithRed_green_blue_alpha_(0.35, 0.18, 0.05, 1.0)
        )
        self.badge_label.setBezeled_(True)
 
        self._tick()
 
    def _add_label(self, parent, text, x, y, w, h, size=12, color=(1, 1, 1), italic=False):
        field = NSTextField.alloc().initWithFrame_(NSMakeRect(x, y, w, h))
        field.setStringValue_(text)
        field.setBezeled_(False)
        field.setDrawsBackground_(False)
        field.setEditable_(False)
        field.setSelectable_(False)
        if italic:
            field.setFont_(NSFont.italicSystemFontOfSize_(size))
        else:
            field.setFont_(NSFont.systemFontOfSize_(size))
        field.setTextColor_(NSColor.colorWithRed_green_blue_alpha_(*color, 1.0))
        parent.addSubview_(field)
        return field
 
    def _update_labels(self, site_name=""):
        if self.window is None:
            return
        if hasattr(self, 'streak_label'):
            self.streak_label.setStringValue_(self._streak_text())
        if site_name and hasattr(self, 'msg_label'):
            self.msg_label.setStringValue_(f"hey, {site_name} isn't it...")
 
    def _update_timer_label(self, text, color=(0.478, 0.416, 0.604)):
        if hasattr(self, 'timer_label') and self.window:
            self.timer_label.setStringValue_(text)
            self.timer_label.setTextColor_(
                NSColor.colorWithRed_green_blue_alpha_(*color, 1.0)
            )
 
    def _tick(self):
        if self.window is None:
            return
        self.countdown -= 1
        if hasattr(self, 'progress_bar'):
            self.progress_bar.setProgress_(self.countdown / self.COUNTDOWN_SECS)
 
        if self.countdown <= 0:
            self._update_timer_label("streak reset!", color=(1.0, 0.29, 0.29))
            self.reset_streak()
            self.countdown_job = self.root.after(2000, self._close_after_reset)
        else:
            self._update_timer_label(f"{self.countdown}s to get back")
            self.countdown_job = self.root.after(1000, self._tick)
 
    def _close_after_reset(self):
        if self.window is not None:
            self.window.orderOut_(None)
            self.window = None
 
    def _streak_text(self):
        mins = int((time.time() - self.streak_start) / 60)
        return f"{mins} min focus streak"
