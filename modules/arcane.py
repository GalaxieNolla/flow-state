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
        self.alpha = max(0.0, min(1.0, self.alpha + direction * 0.08))
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

        # Get button position from canvas
        coords = self.canvas.coords(self.bg_id)
        if not coords:
            return
        cx, cy = coords[0], coords[1]

        a = self.alpha  # 0–1

        # Choose stipple based on alpha
        if a < 0.33:
            stipple = "gray12"
        elif a < 0.66:
            stipple = "gray25"
        elif a < 0.9:
            stipple = "gray50"
        else:
            stipple = ""

        self._draw_ring(cx, cy, 130, self.angle1,  stipple, a)
        self._draw_ring(cx, cy, 95,  self.angle2,  stipple, a)
        self._draw_ring(cx, cy, 60,  self.angle3,  stipple, a)

        # Raise button above circle
        self.canvas.tag_raise(self.bg_id)
        self.canvas.tag_raise(self.txt_id)

    def _draw_ring(self, cx, cy, r, angle_offset, stipple, a):
        tag = self.tag

        # Outer circle
        self.canvas.create_oval(
            cx - r, cy - r, cx + r, cy + r,
            outline=self.col_outer if r == 130 else (self.col_mid if r == 95 else self.col_inner),
            width=1 if r < 130 else 2,
            fill="", tags=tag
        )

        # Nodes & polygon for outer ring only
        if r == 130:
            n_points = 6
            nodes = []
            for i in range(n_points):
                ang = math.radians(angle_offset + i * 360 / n_points)
                nx = cx + r * math.cos(ang)
                ny = cy + r * math.sin(ang)
                nodes.append((nx, ny))
                self.canvas.create_oval(
                    nx - 4, ny - 4, nx + 4, ny + 4,
                    outline=self.col_node, width=1, fill="", tags=tag
                )
            # Two overlapping triangles (Star of David style)
            t1 = [nodes[0], nodes[2], nodes[4]]
            t2 = [nodes[1], nodes[3], nodes[5]]
            for tri in (t1, t2):
                pts = [c for p in tri for c in p]
                self.canvas.create_polygon(
                    *pts, outline=self.col_poly,
                    fill="", width=1, tags=tag
                )

        # Triangle for mid ring
        if r == 95:
            n_points = 3
            pts = []
            for i in range(n_points):
                ang = math.radians(angle_offset + i * 120)
                pts.extend([cx + r * math.cos(ang), cy + r * math.sin(ang)])
            self.canvas.create_polygon(
                *pts, outline=self.col_poly,
                fill="", width=1, tags=tag
            )

        # Runic text around outer ring
        if r == 130:
            n_runes = 24
            for i in range(n_runes):
                ang = math.radians(angle_offset + i * (360 / n_runes))
                rx = cx + (r + 10) * math.cos(ang)
                ry = cy + (r + 10) * math.sin(ang)
                rune = RUNES[i % len(RUNES)]
                self.canvas.create_text(
                    rx, ry, text=rune,
                    font=("Arial", 7), fill=self.col_rune,
                    tags=tag
                )

        # Runic text around mid ring  
        if r == 95:
            n_runes = 16
            for i in range(n_runes):
                ang = math.radians(angle_offset + i * (360 / n_runes))
                rx = cx + (r - 12) * math.cos(ang)
                ry = cy + (r - 12) * math.sin(ang)
                rune = RUNES[(i + 8) % len(RUNES)]
                self.canvas.create_text(
                    rx, ry, text=rune,
                    font=("Arial", 6), fill=self.col_rune,
                    tags=tag
                )
