import tkinter as tk
import math

RUNES = "ᚠᚢᚦᚨᚱᚲᚷᚹᚺᚾᛁᛃᛇᛈᛉᛋᛏᛒᛖᛗᛚᛜᛞᛟ"

class Arcane:
    """
    RUNES I.E. THE ARCANE, z-ordered behind buttons.
    """

    def __init__(self, canvas, bg_id, txt_id, color="blue"):
        self.canvas = canvas
        self.bg_id = bg_id
        self.txt_id = txt_id
        self.tag = f"mc_{id(self)}"
        self.scale = 1.0 # to help readjust for screen resize

        # blue = time-based, purple = task-based
        if color == "blue":
            self.col_outer  = "#1a6fff"
            self.col_mid    = "#0a4fc0"
            self.col_inner  = "#083090"
            self.col_rune   = "#2060c0"
            self.col_poly   = "#1a50c0"
            self.col_node   = "#3080ff"
        else:
            self.col_outer  = "#8020ff"
            self.col_mid    = "#7010d0"
            self.col_inner  = "#4010a0"
            self.col_rune   = "#6020b0"
            self.col_poly   = "#6020c0"
            self.col_node   = "#9040ff"

        self.alpha       = 0.0      # 0.0 – 1.0 logical opacity (simulated via stipple)
        self.visible     = False
        self.angle1      = 0.0      # outer ring rotation
        self.angle2      = 0.0      # mid ring (counter)
        self.angle3      = 0.0      # inner ring
        self._anim_id    = None
        self._fade_id    = None

        # Bind hover on both image and text items
        for item in (bg_id, txt_id):
            canvas.tag_bind(item, "<Enter>", self._on_enter)
            canvas.tag_bind(item, "<Leave>", self._on_leave)

    # ── Public ────────────────────────────────────────────────────────────────

    def destroy(self):
        self._stop()
        self.canvas.delete(self.tag)

    # ── Hover callbacks ───────────────────────────────────────────────────────

    def _on_enter(self, event):
        self.visible = True
        self._cancel_fade()
        self._fade_step(direction=1)
        if self._anim_id is None:
            self._animate()

    def _on_leave(self, event):
        self.visible = False
        self._cancel_fade()
        self._fade_step(direction=-1)

    # ── Fade ──────────────────────────────────────────────────────────────────

    def _cancel_fade(self):
        if self._fade_id:
            self.canvas.after_cancel(self._fade_id)
            self._fade_id = None

    def _fade_step(self, direction):
        self.alpha = max(0.0, min(0.6, self.alpha + direction * 0.08)) #0.6 = slightly less opaque
        self._draw()
        if (direction == 1 and self.alpha < 1.0) or (direction == -1 and self.alpha > 0.0):
            self._fade_id = self.canvas.after(16, lambda: self._fade_step(direction))
        else:
            self._fade_id = None
            if self.alpha == 0.0:
                self._stop()

    # ── Animation loop ────────────────────────────────────────────────────────

    def _animate(self):
        self.angle1 = (self.angle1 + 0.4) % 360
        self.angle2 = (self.angle2 - 0.25) % 360
        self.angle3 = (self.angle3 + 0.15) % 360
        self._draw()
        if self.alpha > 0:
            self._anim_id = self.canvas.after(16, self._animate)
        else:
            self._anim_id = None

    def _stop(self):
        if self._anim_id:
            self.canvas.after_cancel(self._anim_id)
            self._anim_id = None

    # ── Drawing ───────────────────────────────────────────────────────────────

    def _draw(self):
        self.canvas.delete(self.tag)
        if self.alpha <= 0:
            return
    
        coords = self.canvas.coords(self.bg_id)
        if not coords:
            return
        cx, cy = coords[0], coords[1]
    
        a = self.alpha
        if a < 0.33:
            stipple = "gray12"
        elif a < 0.66:
            stipple = "gray25"
        elif a < 0.9:
            stipple = "gray50"
        else:
            stipple = ""
    
        r_outer = int(130 * self.scale)
        r_mid   = int(95  * self.scale)
        r_inner = int(60  * self.scale)
    
        rune_font_outer = max(6, int(8 * self.scale))   # add these
        rune_font_mid   = max(5, int(7 * self.scale))
    
        self._draw_ring(cx, cy, r_outer, self.angle1, stipple, a, rune_font_outer, is_outer=True)
        self._draw_ring(cx, cy, r_mid,   self.angle2, stipple, a, rune_font_mid,   is_mid=True)
        self._draw_ring(cx, cy, r_inner, self.angle3, stipple, a, 0)
    
        self.canvas.tag_raise(self.bg_id)
        self.canvas.tag_raise(self.txt_id)

    def _draw_ring(self, cx, cy, r, angle_offset, stipple, a, rune_font=7, is_outer=False, is_mid=False):
        tag = self.tag
    
        self.canvas.create_oval(
            cx - r, cy - r, cx + r, cy + r,
            outline=self.col_outer if is_outer else (self.col_mid if is_mid else self.col_inner),
            width=2 if is_outer else 1,
            fill="", tags=tag
        )
    
        if is_outer:
            n_points = 6
            nodes = []
            for i in range(n_points):
                ang = math.radians(angle_offset + i * 60)
                nx = cx + r * math.cos(ang)
                ny = cy + r * math.sin(ang)
                nodes.append((nx, ny))
                self.canvas.create_oval(nx-3, ny-3, nx+3, ny+3,
                    outline=self.col_node, width=1, fill="", tags=tag)
            t1 = [nodes[0], nodes[2], nodes[4]]
            t2 = [nodes[1], nodes[3], nodes[5]]
            for tri in (t1, t2):
                pts = [c for p in tri for c in p]
                self.canvas.create_polygon(*pts, outline=self.col_poly, fill="", width=1, tags=tag)
    
            # Runes just inside the outer ring
            for i in range(24):
                ang = math.radians(angle_offset + i * 15)
                rx = cx + (r - 12) * math.cos(ang)   # inside the ring, not outside
                ry = cy + (r - 12) * math.sin(ang)
                self.canvas.create_text(rx, ry, text=RUNES[i % len(RUNES)],
                    font=("Arial", rune_font), fill=self.col_rune, tags=tag)
    
        if is_mid:
            pts = []
            for i in range(3):
                ang = math.radians(angle_offset + i * 120)
                pts.extend([cx + r * math.cos(ang), cy + r * math.sin(ang)])
            self.canvas.create_polygon(*pts, outline=self.col_poly, fill="", width=1, tags=tag)
    
            # Runes inside mid ring
            for i in range(12):
                ang = math.radians(angle_offset + i * 30)
                rx = cx + (r - 10) * math.cos(ang)
                ry = cy + (r - 10) * math.sin(ang)
                self.canvas.create_text(rx, ry, text=RUNES[(i + 8) % len(RUNES)],
                    font=("Arial", rune_font), fill=self.col_rune, tags=tag)
