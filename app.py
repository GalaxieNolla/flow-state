def open(self):
    if self.window and self.window.winfo_exists():
        self.window.lift()
        return

    self.window = tk.Toplevel(self.root)
    self.window.title("Leaderboard")
    self.window.configure(bg=styles.BG_DARK)
    self.window.attributes("-topmost", True)

    # background
    bg_path = os.path.join(os.path.dirname(__file__), "..", "visuals", "leader background.png")
    bg_img = Image.open(bg_path).resize((1100, 580), Image.Resampling.LANCZOS)
    self.bg_image = ImageTk.PhotoImage(bg_img)
    W, H = bg_img.width, bg_img.height

    self.window.geometry(f"{W}x{H}")
    self.canvas = tk.Canvas(self.window, width=W, height=H, highlightthickness=0, bg=styles.BG_DARK)
    self.canvas.pack(fill="both", expand=True)
    self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")

    panel_w = 460
    panel_h = 480
    left_x = 80
    right_x = 580
    panel_y = 60

    left_img = Image.open(os.path.join(VISUALS_DIR, "left-blue.png")).convert("RGBA")
    left_img = left_img.resize((panel_w, panel_h), Image.Resampling.LANCZOS)
    self.left_panel_img = ImageTk.PhotoImage(left_img)
    self.canvas.create_image(left_x, panel_y, image=self.left_panel_img, anchor="nw")

    right_img = Image.open(os.path.join(VISUALS_DIR, "right-pink.png")).convert("RGBA")
    right_img = right_img.resize((panel_w, panel_h), Image.Resampling.LANCZOS)
    self.right_panel_img = ImageTk.PhotoImage(right_img)
    self.canvas.create_image(right_x, panel_y, image=self.right_panel_img, anchor="nw")

    lc = left_x + panel_w // 2
    rc = right_x + panel_w // 2

    self.canvas.create_text(lc, panel_y + 30, text="✦ Winner's Circle ✦",
        font=("Cinzel", 15, "bold"), fill=styles.JINX_BLUE)
    self.canvas.create_text(rc, panel_y + 30, text="✦ Current Session ✦",
        font=("Cinzel", 15, "bold"), fill="#e8a0c0")

    self.canvas.create_line(left_x + 30, panel_y + 50, left_x + panel_w - 30, panel_y + 50,
        fill=styles.JINX_BLUE, width=1)
    self.canvas.create_line(right_x + 30, panel_y + 50, right_x + panel_w - 30, panel_y + 50,
        fill="
