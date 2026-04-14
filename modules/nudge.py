import time
import AppKit
from AppKit import (
    NSWindowStyleMaskBorderless, NSBackingStoreBuffered,
    NSColor, NSTextField, NSFont, NSMakeRect, NSFloatingWindowLevel,
    NSWindowCollectionBehaviorCanJoinAllSpaces,
    NSWindowCollectionBehaviorStationary,
    NSNonactivatingPanelMask, NSPanel, NSView,
    NSFontManager, NSItalicFontMask
)

W = 240
H = 120

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
        # streak NOT reset here — only on full timeout

    def reset_streak(self):
        self.streak_start = time.time()

    def _create_window(self, site_name):
        screen = AppKit.NSScreen.mainScreen()
        sw = screen.frame().size.width
        sh = screen.frame().size.height
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

        # row 1: fire + streak  (y=92)
        self._add_label(cv, "🔥", 14, 92, 28, 22, size=16)
        self.streak_label = self._add_label(
            cv, self._streak_text(), 44, 94, 180, 18,
            size=11, color=(0.765, 0.478, 1.0)
        )

        # row 2: distraction message  (y=68)
        self.msg_label = self._add_label(
            cv, f"hey, {site_name} isn't it...", 14, 68, W - 28, 18,
            size=10, color=(1.0, 0.42, 0.42), italic=True
        )

        # row 3: progress bar track + fill  (y=54)
        bar_x, bar_y, bar_w, bar_h = 14, 54, W - 28, 5
        track = NSView.alloc().initWithFrame_(NSMakeRect(bar_x, bar_y, bar_w, bar_h))
        track.setWantsLayer_(True)
        track.layer().setBackgroundColor_(
            NSColor.colorWithRed_green_blue_alpha_(0.2, 0.15, 0.3, 1.0).CGColor()
        )
        track.layer().setCornerRadius_(2.5)
        cv.addSubview_(track)

        self.bar_fill = NSView.alloc().initWithFrame_(NSMakeRect(bar_x, bar_y, bar_w, bar_h))
        self.bar_fill.setWantsLayer_(True)
        self.bar_fill.layer().setBackgroundColor_(
            NSColor.colorWithRed_green_blue_alpha_(0.53, 0.35, 0.85, 1.0).CGColor()
        )
        self.bar_fill.layer().setCornerRadius_(2.5)
        cv.addSubview_(self.bar_fill)

        # row 4: timer label  (y=34)
        self.timer_label = self._add_label(
            cv, f"{self.countdown}s to get back", 14, 34, W - 28, 16,
            size=9, color=(0.478, 0.416, 0.604)
        )

        # row 5: distracted badge  (y=10)
        self.badge_label = self._add_label(
            cv, "  distracted  ", 14, 10, 88, 18,
            size=9, color=(0.9, 0.55, 0.25)
        )
        self.badge_label.setDrawsBackground_(True)
        self.badge_label.setBackgroundColor_(
            NSColor.colorWithRed_green_blue_alpha_(0.3, 0.14, 0.04, 1.0)
        )

        self._tick()

    def _make_italic_font(self, size):
        base = NSFont.systemFontOfSize_(size)
        fm = NSFontManager.sharedFontManager()
        italic = fm.convertFont_toHaveTrait_(base, NSItalicFontMask)
        # fallback: if font manager couldn't make it italic, just return base
        return italic if italic else base

    def _add_label(self, parent, text, x, y, w, h, size=12, color=(1, 1, 1), italic=False):
        field = NSTextField.alloc().initWithFrame_(NSMakeRect(x, y, w, h))
        field.setStringValue_(text)
        field.setBezeled_(False)
        field.setDrawsBackground_(False)
        field.setEditable_(False)
        field.setSelectable_(False)
        if italic:
            field.setFont_(self._make_italic_font(size))
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

    def _update_bar(self, progress):
        if not hasattr(self, 'bar_fill') or self.window is None:
            return
        filled_w = max(2, int((W - 28) * progress))
        self.bar_fill.setFrame_(NSMakeRect(14, 54, filled_w, 5))

    def _tick(self):
        if self.window is None:
            return
        self.countdown -= 1
        self._update_bar(self.countdown / self.COUNTDOWN_SECS)

        if self.countdown <= 0:
            self.timer_label.setStringValue_("streak reset!")
            self.timer_label.setTextColor_(
                NSColor.colorWithRed_green_blue_alpha_(1.0, 0.29, 0.29, 1.0)
            )
            self.reset_streak()
            self.countdown_job = self.root.after(2000, self._close_after_reset)
        else:
            self.timer_label.setStringValue_(f"{self.countdown}s to get back")
            self.countdown_job = self.root.after(1000, self._tick)

    def _close_after_reset(self):
        if self.window is not None:
            self.window.orderOut_(None)
            self.window = None

    def _streak_text(self):
        mins = int((time.time() - self.streak_start) / 60)
        return f"{mins} min focus streak"
