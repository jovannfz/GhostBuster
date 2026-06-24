# ══════════════════════════════════════════════════════════════════
#  SCREENS — BASE
# ══════════════════════════════════════════════════════════════════

class BaseScreen(tk.Frame):
    BG      = "#0a0f1e"
    C_PRI   = "#a8d8ff"
    C_ACC   = "#f9d423"
    C_DNG   = "#ff416c"
    C_TXT   = "#e8e8e8"
    C_MUT   = "#666"
    C_CARD  = "#0d1a2e"
    F_TITLE = ("Courier New", 42, "bold")
    F_HEAD  = ("Courier New", 20, "bold")
    F_BODY  = ("Courier New", 15)
    F_SM    = ("Courier New", 12)

    def __init__(self, parent, controller):
        super().__init__(parent, bg=self.BG)
        self.controller = controller

    def on_show(self): pass


# ══════════════════════════════════════════════════════════════════
#  SCREEN — MENU UTAMA
# ══════════════════════════════════════════════════════════════════

class MenuScreen(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self._build()

    def _build(self):
        self.columnconfigure(0, weight=1)

        tk.Label(self, text="👻  🌙  👻  🌙  👻",
                 font=("Courier New", 18), bg=self.BG, fg="#334").grid(row=0, column=0, pady=(60, 0))

        tk.Label(self, text="GHOSTBUSTERS",
                 font=("Courier New", 54, "bold"),
                 bg=self.BG, fg=self.C_PRI).grid(row=1, column=0, pady=(8, 2))

        tk.Label(self, text="Bust Ghosts. Save the Night.",
                 font=("Courier New", 17), bg=self.BG, fg=self.C_ACC).grid(row=2, column=0, pady=(0, 36))

        self._welcome = tk.StringVar(value="Selamat datang!")
        tk.Label(self, textvariable=self._welcome,
                 font=self.F_HEAD, bg=self.BG, fg=self.C_TXT).grid(row=3, column=0, pady=(0, 26))

        btns = [
            ("▶  MULAI GAME",   self.C_PRI, "#000",     lambda: self.controller.show("GameScreen")),
            ("🏆  LEADERBOARD", self.C_ACC, "#000",     lambda: self.controller.show("LeaderboardScreen")),
            ("⚙  PENGATURAN",  "#1e4d2b",  self.C_TXT, lambda: self.controller.show("SettingsScreen")),
            ("🚪  KELUAR",      self.C_DNG, "#fff",     self.controller.quit),
        ]
        for i, (text, bg, fg, cmd) in enumerate(btns):
            tk.Button(self, text=text, font=self.F_HEAD, width=30,
                      pady=13, bg=bg, fg=fg, relief="flat", cursor="hand2",
                      command=cmd).grid(row=4 + i, column=0, pady=8)

        tk.Label(self, text="👻  💀  👻  💀  👻",
                 font=("Courier New", 16), bg=self.BG, fg="#222").grid(row=8, column=0, pady=(28, 0))

    def on_show(self):
        u = self.controller.current_user
        if u:
            self._welcome.set(f"Halo, {u['username']}! 👋")


# ══════════════════════════════════════════════════════════════════
#  SCREEN — GAME UTAMA
# ══════════════════════════════════════════════════════════════════

CW      = 1240   # lebar canvas (disesuaikan untuk window 1280px)
CH      = 500    # tinggi canvas (disesuaikan untuk window 600px)
FPS_MS  = 16     # ~62 fps
WORLD_W = 3600

PLATFORMS = [
    (0,    380, 3600, 90),
    (220,  300,  180, 18),
    (480,  250,  200, 18),
    (760,  200,  180, 18),
    (1020, 260,  140, 18),
    (1240, 190,  240, 18),
    (1560, 230,  180, 18),
    (1820, 150,  210, 18),
    (2100, 210,  180, 18),
    (2360, 120,  220, 18),
    (2640, 190,  180, 18),
    (2880, 110,  200, 18),
    (3120, 180,  180, 18),
    (3360, 100,  220, 18),
    (600,  335,   80, 45),
    (1400, 325,   80, 55),
    (2800, 320,   80, 60),
]

COIN_POS = [
    (280, 265, False), (400, 220, False), (560, 215, True),  (700, 170, False),
    (840, 165, False), (960, 230, True),  (1100, 225, False),(1300, 155, False),
    (1450, 155, True), (1620, 195, False),(1760, 195, False),(1900, 115, True),
    (2060, 115, False),(2200, 115, False),(2430,  85, True), (2580,  85, False),
    (2720, 155, False),(2860, 155, True), (3000,  75, False),(3160, 145, False),
    (3300, 145, True), (3440,  65, False),
]

GHOST_POS = [
    (420, 220, 0), (680, 170, 1), (900, 170, 0), (1180, 160, 2),
    (1380, 160, 0),(1700, 120, 1),(1960, 180, 0),(2240,  90, 2),
    (2500, 160, 0),(2760, 160, 1),(3020,  80, 0),(3260, 150, 2),
    (3480,  70, 1),(3550, 120, 0),
]

PLATAT_RECTS = [(p[0], p[1], p[0] + p[2], p[1] + p[3]) for p in PLATFORMS]


def _draw_ghost(c, x, y, color, anim, hp, max_hp):
    c.create_oval(x - 18, y - 24, x + 18, y + 2, fill=color, outline="")
    pts = [x - 18, y]
    for i in range(7):
        bx = x - 18 + (i / 6) * 36
        bw = 7 if i % 2 == 0 else -7
        pts += [bx, y + 20 + bw]
    pts += [x + 18, y]
    c.create_polygon(pts, fill=color, outline="")
    c.create_rectangle(x - 11, y - 14, x - 5,  y - 7,  fill="#222", outline="")
    c.create_rectangle(x + 5,  y - 14, x + 11, y - 7,  fill="#222", outline="")
    if max_hp > 1:
        c.create_rectangle(x - 18, y - 32, x + 18, y - 27, fill="#c00", outline="")
        fw = int(36 * hp / max_hp)
        c.create_rectangle(x - 18, y - 32, x - 18 + fw, y - 27, fill="#3f3", outline="")


def _draw_player(c, x, y, w, h, on_ground, frame):
    c.create_oval(x + 2, y + h + 2, x + w - 2, y + h + 10, fill="#333", outline="")
    c.create_oval(x, y, x + w, y + h // 2 + 8, fill="#e8e8f0", outline="#aaa", width=1)
    pts = [x, y + h // 2 + 2, x, y + h]
    for i in range(6):
        bx = x + (i / 5) * w
        bv = 6 if i % 2 == 0 else -6
        pts += [bx, y + h + bv]
    pts += [x + w, y + h // 2 + 2]
    c.create_polygon(pts, fill="#e8e8f0", outline="")
    c.create_rectangle(x + 6,  y + 5,  x + 12, y + 12, fill="#222", outline="")
    c.create_rectangle(x + 18, y + 5,  x + 24, y + 12, fill="#222", outline="")
    c.create_arc(x + 8, y + 12, x + 22, y + 20, start=200, extent=140,
                 style="arc", outline="#444", width=2)


class GameScreen(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.lv_mgr = LevelManager()
        self.sc_mgr = ScoreManager()
        self.player = PlayerPhysics()

        self._running    = False
        self._paused     = False
        self._transition = False
        self._after      = None
        self._timer      = 120
        self._lives      = 3
        self._cam_x      = 0.0
        self._frame      = 0
        self._ghosts     = []
        self._coins      = []
        self._projs      = []
        self._parts      = []
        self._keys       = {"left": False, "right": False, "jump": False, "fire": False}
        self._fire_cd    = 0

        self._build_ui()

    def _build_ui(self):
        hud = tk.Frame(self, bg=self.BG)
        hud.pack(fill="x", padx=14, pady=(6, 2))

        self._lv_var = tk.StringVar(value="Level 1 — Easy")
        self._sc_var = tk.StringVar(value="Skor: 0")
        self._tm_var = tk.StringVar(value="⏱ 120")
        self._hp_var = tk.StringVar(value="❤ ❤ ❤")

        tk.Label(hud, textvariable=self._lv_var, font=self.F_HEAD,
                 bg=self.BG, fg=self.C_PRI).pack(side="left", padx=14)
        tk.Label(hud, textvariable=self._sc_var, font=self.F_HEAD,
                 bg=self.BG, fg=self.C_ACC).pack(side="left", padx=14)
        tk.Label(hud, textvariable=self._tm_var, font=self.F_HEAD,
                 bg=self.BG, fg="#fff").pack(side="left", padx=14)
        tk.Label(hud, textvariable=self._hp_var, font=self.F_HEAD,
                 bg=self.BG, fg=self.C_DNG).pack(side="right", padx=14)

        self._cv = tk.Canvas(self, width=CW, height=CH,
                             bg="#1a2a5e", highlightthickness=2,
                             highlightbackground=self.C_PRI)
        self._cv.pack(padx=14)

        ctrl = tk.Frame(self, bg=self.BG)
        ctrl.pack(fill="x", padx=14, pady=4)

        tk.Label(ctrl, text="Arrow/WASD = Gerak  |  Space/W/↑ = Lompat  |  Z/X = Tembak",
                 font=self.F_SM, bg=self.BG, fg="#555").pack(side="left", padx=8)

        self._pause_btn = tk.Button(ctrl, text="⏸ Pause",
                                    font=self.F_BODY, bg=self.C_ACC, fg="#000",
                                    relief="flat", cursor="hand2",
                                    command=self._toggle_pause)
        self._pause_btn.pack(side="left", padx=6)

        tk.Button(ctrl, text="🏠 Menu", font=self.F_BODY,
                  bg=self.C_DNG, fg="#fff", relief="flat", cursor="hand2",
                  command=self._back_menu).pack(side="right", padx=6)

        self.bind_all("<KeyPress>",   self._key_down)
        self.bind_all("<KeyRelease>", self._key_up)

    def _key_down(self, e):
        k = e.keysym
        if k in ("Left",  "a", "A"):        self._keys["left"]  = True
        if k in ("Right", "d", "D"):        self._keys["right"] = True
        if k in ("space", "Up", "w", "W"):  self._keys["jump"]  = True
        if k in ("z", "Z", "x", "X"):       self._keys["fire"]  = True

    def _key_up(self, e):
        k = e.keysym
        if k in ("Left",  "a", "A"):        self._keys["left"]  = False
        if k in ("Right", "d", "D"):        self._keys["right"] = False
        if k in ("space", "Up", "w", "W"):  self._keys["jump"]  = False
        if k in ("z", "Z", "x", "X"):       self._keys["fire"]  = False

    def on_show(self):
        self.lv_mgr.reset()
        self._init_level()

    def _init_level(self):
        cfg = self.lv_mgr.cfg()
        self.sc_mgr = ScoreManager(mult=cfg["mult"])
        self.player = PlayerPhysics()
        self.player.GROUND_Y  = GROUND_Y - self.player.H
        self.player.y         = float(self.player.GROUND_Y)
        self.player.x         = 80.0
        self.player.platforms = PLATAT_RECTS

        self._running    = True
        self._paused     = False
        self._transition = False
        self._timer      = cfg["timer"]
        self._lives      = 3
        self._cam_x      = 0.0
        self._frame      = 0
        self._fire_cd    = 0

        n = cfg["hantu"]
        self._ghosts = [GhostAI(gx, gy, cfg["kecepatan"], gt) for gx, gy, gt in GHOST_POS[:n]]
        self._coins  = [CoinItem(cx, cy, gem) for cx, cy, gem in COIN_POS]
        self._projs  = []
        self._parts  = []

        self._cv.config(bg=self.lv_mgr.theme()["sky"])
        self._update_hud()
        self._timer_tick()
        self._loop()

    def _loop(self):
        if not self._running or self._paused or self._transition:
            return
        self._update()
        self._draw()
        self._after = self.after(FPS_MS, self._loop)