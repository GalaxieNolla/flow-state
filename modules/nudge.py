import tkinter as tk
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
import objc
import random
import webbrowser

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
        self.monitor = monitor

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
        if hasattr(self, 'overlay') and self.overlay:
            self.overlay.destroy()
            self.overlay = None
        if hasattr(self, 'countdown_job_click'):
            self.root.after_cancel(self.countdown_job_click)
            self.countdown_job_click = None

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
        self.window.setBackgroundColor_(NSColor.clearColor())
        cv.layer().setMasksToBounds_(True)
        cv.layer().setBackgroundColor_(
            NSColor.colorWithRed_green_blue_alpha_(0.071, 0.035, 0.129, 0.95).CGColor()
        )

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
        # (1) stress button
        self.stressed_view = ClickableView.alloc().initWithFrame_callback_(
            NSMakeRect(14, 8, 72, 20), self._on_stressed
        )
        self.stressed_view.setWantsLayer_(True)
        self.stressed_view.layer().setBackgroundColor_(
            NSColor.colorWithRed_green_blue_alpha_(0.18, 0.1, 0.3, 1.0).CGColor()
        )
        self.stressed_view.layer().setCornerRadius_(4)
        cv.addSubview_(self.stressed_view)
        self._add_label(self.stressed_view, "stressed", 4, 2, 64, 16, size=9, color=(0.6, 0.4, 1.0))

        # (2) break button
        self.break_view = ClickableView.alloc().initWithFrame_callback_(
            NSMakeRect(92, 8, 90, 20), self._on_break
        )
        self.break_view.setWantsLayer_(True)
        self.break_view.layer().setBackgroundColor_(
            NSColor.colorWithRed_green_blue_alpha_(0.05, 0.25, 0.18, 1.0).CGColor()
        )
        self.break_view.layer().setCornerRadius_(4)
        cv.addSubview_(self.break_view)
        self._add_label(self.break_view, "take a break", 4, 2, 82, 16, size=9, color=(0.2, 0.8, 0.55))

        self._tick()
        self._start_click_polling()

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
        # interpolate purple (0.53, 0.35, 0.85) → red (1.0, 0.29, 0.29)
        r = 0.53 + (1.0 - 0.53) * (1 - progress)
        g = 0.35 + (0.29 - 0.35) * (1 - progress)
        b = 0.85 + (0.29 - 0.85) * (1 - progress)
        self.bar_fill.layer().setBackgroundColor_(
            NSColor.colorWithRed_green_blue_alpha_(r, g, b, 1.0).CGColor()
        )

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

    def _create_button_overlay(self):
        if self.window is None:
            return
        elif hasattr(self, 'overlay') and self.overlay:
            return
        screen = AppKit.NSScreen.mainScreen()
        sw = screen.frame().size.width
        sh = screen.frame().size.height
        
        # AppKit y is from bottom, tkinter from top
        win_x = int(sw - W - 20)
        tkinter_y = int(sh - (sh - H - 20) - 28)
        self.overlay.geometry(f"{W}x50+{win_x}+{tkinter_y}")
        print(f"overlay at: {win_x}, {tkinter_y}, sh={sh}") #debug
    
        self.overlay = tk.Toplevel(self.root)
        self.overlay.overrideredirect(True)
        self.overlay.attributes("-topmost", True)
        self.overlay.attributes("-transparent", True)
        self.overlay.configure(bg="systemTransparent")
        self.overlay.geometry(f"{W}x30+{win_x}+{tkinter_y}")  # sits at bottom of nudge
        print(f"overlay at: {win_x}, {tkinter_y}, screen height: {sh}")
    
        stressed_btn = tk.Button(
            self.overlay, text="stressed", font=("Helvetica", 9),
            bg="#2e1a4d", fg="#a066ff", relief="flat", padx=6, pady=2,
            activebackground="#3d2060", activeforeground="#c39fff",
            command=self._on_stressed
        )
        stressed_btn.pack(side="left", padx=(8, 4), pady=4)
    
        break_btn = tk.Button(
            self.overlay, text="take a break", font=("Helvetica", 9),
            bg="#0d3d2a", fg="#33cc99", relief="flat", padx=6, pady=2,
            activebackground="#0f4f36", activeforeground="#55ffbb",
            command=self._on_break
        )
        break_btn.pack(side="left", padx=(0, 4), pady=4)

    STRESSED_MESSAGES = [
    "you're doing better than you think 💜",
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
    ]
    
    def _on_stressed(self):
        webbrowser.open("https://www.calm.com/breathe")
        self._show_message_popup(
            random.choice(self.STRESSED_MESSAGES), color=(0.6, 0.4, 1.0)
        )
        self._breathing_mode = True
        self._last_breathe_remind = time.time()
        self._poll_breathing()

    def _poll_breathing(self):
        if not getattr(self, '_breathing_mode', False):
            return
        idle = self.root.master.monitor.get_idle_time() if hasattr(self.root, 'master') else None
        idle = self._get_idle()
        if idle is not None and idle < 2:  # mouse moved
            now = time.time()
            if now - self._last_breathe_remind > 10:  # don't spam
                self._show_message_popup("hey, try to stay still and breathe 🫶", color=(0.6, 0.4, 1.0))
                self._last_breathe_remind = now
        self.root.after(1000, self._poll_breathing)

    def _stop_breathing_mode(self):
        self._breathing_mode = False

    def _get_idle(self):
        try:
            return self.monitor.get_idle_time()
        except:
            return None

    def _on_break(self):
        # pause the nudge for 5 minutes
        if self.countdown_job:
            self.root.after_cancel(self.countdown_job)
            self.countdown_job = None
        if self.window is not None:
            self.window.orderOut_(None)
            self.window = None
        self.countdown = 0
        self._show_message_popup(
            random.choice(self.BREAK_MESSAGES), color=(0.2, 0.8, 0.55)
        )
        # re-enable nudging after 5 minutes
        self.root.after(300_000, self._end_break)
    
    def _end_break(self):
        self._last_shown = 0  # reset cooldown so nudge can show again
    
    def _show_message_popup(self, message, color=(1,1,1)):
        screen = AppKit.NSScreen.mainScreen()
        sw = screen.frame().size.width
        sh = screen.frame().size.height
        PW, PH = 260, 50
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
        self._add_label(cv, message, 12, 15, PW - 24, 22, size=10, color=color)
        popup.makeKeyAndOrderFront_(None)
        popup.resignKeyWindow()
    
        # auto-dismiss after 4 seconds
        self.root.after(4000, lambda: popup.orderOut_(None))

    def _start_click_polling(self):
        if self.window is None:
            return
        try:
            pos = AppKit.NSEvent.mouseLocation()
            frame = self.window.frame()
            # translate to window-local coords
            local_x = pos.x - frame.origin.x
            local_y = pos.y - frame.origin.y
            # check if mouse is down
            pressed = AppKit.NSEvent.pressedMouseButtons() & 1
    
            if pressed:
                # stressed button rect: x=14-86, y=8-28
                if 14 <= local_x <= 86 and 8 <= local_y <= 28:
                    self._on_stressed()
                    return
                # break button rect: x=92-182, y=8-28
                if 92 <= local_x <= 182 and 8 <= local_y <= 28:
                    self._on_break()
                    return
        except Exception as e:
            print(f"click poll error: {e}")
        self.countdown_job_click = self.root.after(100, self._start_click_polling)
