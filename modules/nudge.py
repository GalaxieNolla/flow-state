import tkinter as tk
import time
import random
import webbrowser
import AppKit
from AppKit import (
    NSWindowStyleMaskBorderless, NSBackingStoreBuffered,
    NSColor, NSTextField, NSFont, NSMakeRect, NSFloatingWindowLevel,
    NSWindowCollectionBehaviorCanJoinAllSpaces,
    NSWindowCollectionBehaviorStationary,
    NSNonactivatingPanelMask, NSPanel, NSView,
    NSFontManager, NSItalicFontMask
)
from visuals import styles

W = 240
H = 120

class Nudge:
    """
    Sends a pop-up on top right corner of screen to users, nudging them to focus. 
    Options to: 1) stop distractions, 2) breathing (stress), 3) take a 5 min break.
    Once an option is selected, a random message from the associated option (stressed or break) will appear as a pop-up below the original nudge.
    """
    COUNTDOWN_SECS = 30

    # Messages to randomly choose from :D
    STRESSED_MESSAGES = [
        "Ekko: 'Sometimes taking a leap forward\rmeans leaving a few things behind.'",
        "Vi: 'You're stronger than you think.'",
        "Viktor: 'When you're going to change\rthe world, don't ask for permission.'",
        "Vi: 'We've all had bad days.\rBut we learn, and we stick together.'",
        "Vander: 'You've got a good heart.\rDon't ever lose it.",
        "Ekko: 'In case I don't remember to tell you\rtomorrow, you've always meant the world to me.'",
        "Jayce: 'There is beauty in imperfections.\rThey made you who you are.'",
        "Vi: 'Be honest. Be patient.'",
        "you're doing better than you think",
        "one thing at a time. breathe.",
        "it's okay to not have it all figured out.",
        "rest is part of the work too.",
        "you've gotten through hard things before.",
    ]

    BREAK_MESSAGES = [
        "stand up and stretch for 2 mins 🧘",
        "go drink a full glass of water 💧",
        "look out a window for 20 seconds 👀",
        "roll your shoulders back. unclench your jaw.",
        "step outside for 5 mins if you can ☀️",
        "Vander: 'You need to fill your own cup\revery now and again.'"
        "Vi: 'You're an all-right shot.'"
        "Jinx: 'Big fat hero ❤︎'"
    ]

    def __init__(self, root, monitor):
        self.root = root
        self.monitor = monitor
        self.window = None
        self.streak_start = time.time()
        self.countdown = 0
        self.countdown_job = None
        self.countdown_job_click = None
        self.is_distracted = False
        self._last_shown = 0
        self._COOLDOWN = 3.0
        self._breathing_mode = False
        self._last_breathe_remind = 0

    # PUBLIC API

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
        if self.countdown_job_click:
            self.root.after_cancel(self.countdown_job_click)
            self.countdown_job_click = None
        if self.window is not None:
            self.window.orderOut_(None)
            self.window = None
        # NOTE: streak NOT reset — only on full timeout (once countdown hits 0)

    def reset_streak(self):
        self.streak_start = time.time()

    # WINDOW CREATION

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
        self.window.setBackgroundColor_(NSColor.clearColor())
        self.window.setCollectionBehavior_(
            NSWindowCollectionBehaviorCanJoinAllSpaces |
            NSWindowCollectionBehaviorStationary
        )

        cv = self.window.contentView()
        cv.setWantsLayer_(True)
        cv.layer().setCornerRadius_(12)
        cv.layer().setMasksToBounds_(True)
        cv.layer().setBackgroundColor_(
            NSColor.colorWithRed_green_blue_alpha_(0.071, 0.035, 0.129, 0.95).CGColor()
        )

        self.window.makeKeyAndOrderFront_(None)
        self.window.resignKeyWindow()

        # row 1: fire + streak  (y=92)
        self._add_label(cv, "🔥", 14, 92, 28, 22, size=16)
        self.streak_label = self._add_label(
            cv, self._streak_text(), 28, 94, 186, 18,
            size=13, color=styles.PURPLE_GLOW #(0.765, 0.478, 1.0)
        )

        # row 2: distraction message  (y=68)
        self.msg_label = self._add_label(
            cv, f"hey, {site_name} isn't it...", 14, 68, W - 28, 18,
            size=10, color=styles.RED_LOCKIN, #(0.9, 0.45, 0.45)
            italic=True
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

        # row 5: stressed + break buttons
        # (1) stressed button
        self.stressed_view = NSView.alloc().initWithFrame_(NSMakeRect(14, 10, 90, 24))
        self.stressed_view.setWantsLayer_(True)
        self.stressed_view.layer().setBackgroundColor_(
            NSColor.colorWithRed_green_blue_alpha_(0.15, 0.1, 0.25, 1.0).CGColor()
        )
        self.stressed_view.layer().setCornerRadius_(6)
        cv.addSubview_(self.stressed_view)
        self._add_label(self.stressed_view, "stressed", 0, 4, 90, 16, size=11, color=styles.RUNE_GLOW) #color=(0.7, 0.6, 0.9))
        
        # (2) break button
        self.break_view = NSView.alloc().initWithFrame_(NSMakeRect(112, 10, 110, 24))
        self.break_view.setWantsLayer_(True)
        self.break_view.layer().setBackgroundColor_(
            NSColor.colorWithRed_green_blue_alpha_(0.2, 0.1, 0.25, 1.0).CGColor()
        )
        self.break_view.layer().setCornerRadius_(6)
        cv.addSubview_(self.break_view)
        self._add_label(self.break_view, "take a break", 0, 4, 110, 16, size=11, color=(0.8, 0.6, 1.0))

        self._tick()
        self._start_click_polling()

    # HELPER FUNCTIONS
    def _make_italic_font(self, size):
        base = NSFont.systemFontOfSize_(size)
        fm = NSFontManager.sharedFontManager()
        italic = fm.convertFont_toHaveTrait_(base, NSItalicFontMask)
        return italic if italic else base

    def _add_label(self, parent, text, x, y, w, h, size=12, color=(1, 1, 1), italic=False):
        field = NSTextField.alloc().initWithFrame_(NSMakeRect(x, y, w, h))
        field.setStringValue_(text)
        field.setBezeled_(False)
        field.setDrawsBackground_(False)
        field.setEditable_(False)
        field.setSelectable_(False)
        field.setAlignment_(AppKit.NSTextAlignmentCenter)
        field.setFont_(self._make_italic_font(size) if italic else NSFont.systemFontOfSize_(size))
    
        if isinstance(color, str):
            color = color.lstrip("#")
            r, g, b = (int(color[i:i+2], 16) / 255.0 for i in (0, 2, 4))
            field.setTextColor_(NSColor.colorWithRed_green_blue_alpha_(r, g, b, 1.0))
        else:
            field.setTextColor_(NSColor.colorWithRed_green_blue_alpha_(*color[:3], 1.0))
    
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
        # interpolate purple (0.53, 0.35, 0.85) → red (1.0, 0.29, 0.29)
        r = 0.53 + (1.0 - 0.53) * (1 - progress)
        g = 0.35 + (0.29 - 0.35) * (1 - progress)
        b = 0.85 + (0.29 - 0.85) * (1 - progress)
        self.bar_fill.layer().setBackgroundColor_(
            NSColor.colorWithRed_green_blue_alpha_(0.45, 0.28, 0.75, 1.0).CGColor()
        )

    def _streak_text(self):
        mins = int((time.time() - self.streak_start) / 60)
        return f"{mins} min focus streak"

    def _get_idle(self):
        try:
            return self.monitor.get_idle_time()
        except:
            return None

    # COUNTDOWN
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

    # CLICK / USER INPUT
    def _start_click_polling(self):
        if self.window is None:
            return
        try:
            pos = AppKit.NSEvent.mouseLocation()
            frame = self.window.frame()
            local_x = pos.x - frame.origin.x
            local_y = pos.y - frame.origin.y
            pressed = AppKit.NSEvent.pressedMouseButtons() & 1

            if pressed:
                if 14 <= local_x <= 104 and 10 <= local_y <= 34:
                    self._on_stressed()
                    return
                if 112 <= local_x <= 222 and 10 <= local_y <= 34:
                    self._on_break()
                    return
        except Exception as e:
            print(f"click poll error: {e}")
        self.countdown_job_click = self.root.after(100, self._start_click_polling)

    # BUTTON HANDLERS
    def _on_stressed(self):
        webbrowser.open("https://www.calm.com/breathe")
        self._show_message_popup(
            random.choice(self.STRESSED_MESSAGES), color=(0.6, 0.4, 1.0)
        )
        self._breathing_mode = True
        self._last_breathe_remind = time.time()
        self._poll_breathing()

    def _on_break(self):
        if self.countdown_job:
            self.root.after_cancel(self.countdown_job)
            self.countdown_job = None
        if self.countdown_job_click:
            self.root.after_cancel(self.countdown_job_click)
            self.countdown_job_click = None
        if self.window is not None:
            self.window.orderOut_(None)
            self.window = None
        self.countdown = 0
        self._last_shown = time.time() + 300  # blocks show() for 5 minutes
        self._show_message_popup(
            random.choice(self.BREAK_MESSAGES), color=(0.2, 0.8, 0.55)
        )

    def _end_break(self):
        self._last_shown = 0

    # REDIRECT TO BREATHING
    def _poll_breathing(self):
        if not self._breathing_mode:
            return
        idle = self._get_idle()
        if idle is not None and idle < 2:
            now = time.time()
            if now - self._last_breathe_remind > 10:
                self._show_message_popup(
                    "hey, try to stay still and breathe 🫶", color=(0.6, 0.4, 1.0)
                )
                self._last_breathe_remind = now
        self.root.after(1000, self._poll_breathing)

    def _stop_breathing_mode(self):
        self._breathing_mode = False

    # MESSAGE POP-UP
    def _show_message_popup(self, message, color=(1, 1, 1)):
        screen = AppKit.NSScreen.mainScreen()
        sw = screen.frame().size.width
        sh = screen.frame().size.height
        PW, PH = 260, 80
        popup = NSPanel.alloc().initWithContentRect_styleMask_backing_defer_(
            NSMakeRect(sw - PW - 20, sh - H - PH - 30, PW, PH),
            NSNonactivatingPanelMask | NSWindowStyleMaskBorderless,
            NSBackingStoreBuffered,
            False
        )
        popup.setLevel_(NSFloatingWindowLevel)
        popup.setOpaque_(False)
        popup.setAlphaValue_(0.95)
        popup.setBackgroundColor_(NSColor.clearColor())

        cv = popup.contentView()
        cv.setWantsLayer_(True)
        cv.layer().setCornerRadius_(10)
        cv.layer().setMasksToBounds_(True)
        cv.layer().setBackgroundColor_(
            NSColor.colorWithRed_green_blue_alpha_(0.071, 0.035, 0.129, 0.95).CGColor()
        )
        
        # Allowance for two-lined messages
        lines = message.split("\r")
        line_h = 18
        total_h = len(lines) * line_h
        start_y = (PH - total_h) // 2
        
        for i, line in enumerate(lines):
            y = start_y + (len(lines) - 1 - i) * line_h
            self._add_label(cv, line, 12, y, PW - 24, line_h, size=10, color=color)
        #self._add_label(cv, message, 12, 15, PW - 24, 22, size=10, color=color)
        
        popup.makeKeyAndOrderFront_(None)
        popup.resignKeyWindow()

        self.root.after(4000, lambda: popup.orderOut_(None))
