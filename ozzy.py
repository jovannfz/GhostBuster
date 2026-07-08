import tkinter as tk
import math

from daffa import (
    LevelManager, ScoreManager, PlayerPhysics,
    GhostAI, CoinItem, Projectile, Particle,
    _rect_collide, GROUND_Y, P_FLOOR
)
from jovan import db_save_score


# ══════════════════════════════════════════════════════════════════
#  KONSTANTA CANVAS & DUNIA
# ══════════════════════════════════════════════════════════════════

CW      = 1330   # lebar canvas
CH      = 580    # tinggi canvas
FPS_MS  = 16     # ~62 fps
WORLD_W = 3600

PLATFORMS = [
    (0,    460, 3600, 90),
    (220,  380,  180, 18),
    (480,  330,  200, 18),
    (760,  280,  180, 18),
    (1020, 340,  140, 18),
    (1240, 270,  240, 18),
    (1560, 310,  180, 18),
    (1820, 230,  210, 18),
    (2100, 290,  180, 18),
    (2360, 200,  220, 18),
    (2640, 270,  180, 18),
    (2880, 190,  200, 18),
    (3120, 260,  180, 18),
    (3360, 180,  220, 18),
    (600,  415,   80, 45),
    (1400, 405,   80, 55),
    (2800, 400,   80, 60),
]

COIN_POS = [
    (280, 345, False), (400, 300, False), (560, 295, False), (700, 250, False),
    (840, 245, False), (960, 310, False), (1100, 305, False),(1300, 235, False),
    (1450, 235, False), (1620, 275, False),(1760, 275, False),(1900, 195, False),
    (2060, 195, False),(2200, 195, False),(2430, 165, False), (2580, 165, False),
    (2720, 235, False),(2860, 235, False), (3000, 155, False),(3160, 225, False),
    (3300, 225, False), (3440, 145, False),
]

GHOST_POS = [
    # Hantu tambahan (y ~432) ditaruh sejajar tanah, di sela-sela hantu
    # yang sudah ada di platform atas -> pemain harus lompat/tembak dari
    # bawah juga, bikin levelnya sedikit lebih susah.
    (420, 300, 0),
    (550, 432, 1),   # NEW - hantu di tanah
    (680, 250, 1), (900, 250, 0),
    (1050, 432, 0),  # NEW - hantu di tanah
    (1180, 240, 2),
    (1380, 240, 0),
    (1550, 432, 2),  # NEW - hantu di tanah
    (1700, 200, 1),(1960, 260, 0),
    (2050, 432, 1),  # NEW - hantu di tanah
    (2240, 170, 2),
    (2500, 240, 0),
    (2650, 432, 0),  # NEW - hantu di tanah
    (2760, 240, 1),(3020, 160, 0),
    (3150, 432, 2),  # NEW - hantu di tanah
    (3260, 230, 2),
    (3480, 150, 1),(3550, 200, 0),
]

PLAT_RECTS = [(p[0], p[1], p[0] + p[2], p[1] + p[3]) for p in PLATFORMS]


# ══════════════════════════════════════════════════════════════════
#  FUNGSI DRAW KARAKTER
# ══════════════════════════════════════════════════════════════════

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


# ══════════════════════════════════════════════════════════════════
#  BASE SCREEN
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
#  SCREEN — GAME UTAMA
# ══════════════════════════════════════════════════════════════════

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

        # Menyimpan progres saat pemain memilih "Kembali ke Menu Utama"
        # dari layar transisi antar-level, supaya bisa ditawarkan pilihan
        # untuk melanjutkan atau mengulang saat kembali bermain.
        self._resume_level = None
        self._resume_score = 0

        self._build_ui()

    def _build_ui(self):
        hud = tk.Frame(self, bg=self.BG)
        hud.pack(fill="x", padx=14, pady=(6, 2))
        self._hud = hud

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

        tk.Label(ctrl, text="Arrow/WASD = Gerak  |  Space/W/↑ = Lompat  |  Z/J = Tembak",
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
        if k in ("z", "Z", "j", "J"):       self._keys["fire"]  = True

    def _key_up(self, e):
        k = e.keysym
        if k in ("Left",  "a", "A"):        self._keys["left"]  = False
        if k in ("Right", "d", "D"):        self._keys["right"] = False
        if k in ("space", "Up", "w", "W"):  self._keys["jump"]  = False
        if k in ("z", "Z", "j", "J"):       self._keys["fire"]  = False

    def _hide_hud(self):
        # Sembunyikan bar Level/Skor/Timer/Nyawa di atas canvas, dipakai
        # saat layar "Lanjutkan Permainan?" atau transisi antar-level
        # ditampilkan, supaya tidak ada info gameplay lama yang nyangkut.
        self._hud.pack_forget()

    def _show_hud(self):
        if not self._hud.winfo_ismapped():
            self._hud.pack(fill="x", padx=14, pady=(6, 2), before=self._cv)

    def on_show(self):
        if self._resume_level and self._resume_level > 1:
            self._show_resume_choice()
        else:
            self.lv_mgr.reset()
            self._init_level()

    def _init_level(self):
        self._show_hud()
        cfg = self.lv_mgr.cfg()
        self.sc_mgr = ScoreManager(mult=cfg["mult"])
        self.player = PlayerPhysics()
        self.player.GROUND_Y  = GROUND_Y - self.player.H
        self.player.y         = float(self.player.GROUND_Y)
        self.player.x         = 80.0
        self.player.platforms = PLAT_RECTS

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
        # _update() bisa memicu _level_done()/_game_end() di tengah jalan,
        # yang mengubah _running/_transition dan menggambar layar lain
        # (mis. layar "Selamat" atau Game Over). Cek ulang di sini supaya
        # _draw() tidak menimpa layar tersebut dengan tampilan gameplay biasa.
        if not self._running or self._transition:
            return
        self._draw()
        self._after = self.after(FPS_MS, self._loop)

    def _update(self):
        self._frame += 1
        cfg = self.lv_mgr.cfg()
        spd = cfg["kecepatan"] / 2.5 * 4.5

        direction = 0
        if self._keys["left"]:  direction = -1
        if self._keys["right"]: direction =  1

        self.player.move(direction, spd)
        self.player.jump(self._keys["jump"])
        self.player.update()

        self.player.x = max(0.0, min(self.player.x, WORLD_W - self.player.W))

        if self.player.x >= WORLD_W - 120:
            self._level_done(); return

        if self.player.y > CH + 100:
            self._player_hit(fatal=True)
            if not self._running: return

        target      = self.player.x - CW // 3
        self._cam_x += (target - self._cam_x) * 0.12
        self._cam_x  = max(0.0, min(self._cam_x, WORLD_W - CW))

        if self._fire_cd > 0:
            self._fire_cd -= 1
        if self._keys["fire"] and self._fire_cd == 0:
            self._fire_cd = 18
            facing = 1 if direction >= 0 else -1
            cx = self.player.x + self.player.W / 2 + facing * 18
            cy = self.player.y + self.player.H / 2
            for _ in range(3):
                self._projs.append(Projectile(cx, cy, facing))

        for p in self._projs:
            p.update()
            if p.life <= 0: continue
            for g in self._ghosts:
                if not g.dead:
                    gr = g.rect()
                    if _rect_collide(p.rect(), gr):
                        p.life = 0
                        g.hit()
                        self._parts.append(Particle(g.x, g.y, "#8ef", 10, 4))
                        if g.dead:
                            self.sc_mgr.ghost_kill(g.cfg["score"])
                            self._parts.append(Particle(g.x, g.y, "#fff", 18, 5))
        self._projs = [p for p in self._projs if p.life > 0]

        for g in self._ghosts:
            g.update(self.player.x)
            if not g.dead:
                gr = g.rect()
                if self.player.collides(gr[0], gr[1], gr[2], gr[3]):
                    self._player_hit()
                    if self.lv_mgr.current == 3:
                        self.sc_mgr.penalty(50)
                    if not self._running: return

        for c in self._coins:
            c.update()
            if not c.taken:
                cr = c.rect()
                if self.player.collides(cr[0], cr[1], cr[2], cr[3]):
                    c.taken = True
                    self.sc_mgr.coin(self.lv_mgr.current)
                    color = "#4dffb0" if c.gem else "#ffd700"
                    self._parts.append(Particle(c.x, c.y, color, 8, 3))

        for pt in self._parts: pt.update()
        self._parts = [pt for pt in self._parts if pt.alive()]
        self._update_hud()

    def _player_hit(self, fatal=False):
        self._lives -= 1
        self._hp_var.set("❤ " * max(self._lives, 0))
        self._parts.append(Particle(
            self.player.x + self.player.W / 2,
            self.player.y + self.player.H / 2, "#f55", 10, 4))

        if self._lives <= 0 or fatal:
            self._game_end(won=False); return

        self.player.x  = max(0, self._cam_x + 80)
        self.player.y  = float(self.player.GROUND_Y)
        self.player.vy = 0
        self.player.vx = 0
        self.player.on_ground = True

    def _level_done(self):
        self._running    = False
        self._transition = True
        self._cancel()
        bonus = self.sc_mgr.time_bonus(self._timer, self.lv_mgr.current)

        if self.lv_mgr.is_last():
            # Level terakhir (Level 3) selesai -> ini yang dianggap "menang",
            # skor baru disimpan ke leaderboard di sini.
            self._game_end(won=True)
        else:
            # Level 1/2 selesai: lanjut ke level berikutnya, TANPA
            # menyimpan skor ke leaderboard (leaderboard hanya untuk
            # yang sudah menyelesaikan seluruh 3 level).
            self.lv_mgr.next()
            self._show_transition(bonus)

    def _save_score_checkpoint(self):
        user = self.controller.current_user
        if user and user.get("id"):
            try:
                db_save_score(user["id"], self.sc_mgr.total, self.lv_mgr.current)
            except Exception:
                pass

    def _show_transition(self, bonus):
        self._hide_hud()
        c       = self._cv
        prev_lv = self.lv_mgr.current - 1
        next_cfg = self.lv_mgr.cfg()

        c.delete("all")
        c.create_rectangle(0, 0, CW, CH, fill="#0a0f1e")
        c.create_text(CW // 2, 100,
                      text=f"✅  Selamat! Level {prev_lv} Selesai!",
                      font=("Courier New", 32, "bold"), fill=self.C_PRI)
        c.create_text(CW // 2, 160,
                      text=f"Bonus Waktu: +{bonus} poin",
                      font=("Courier New", 20), fill=self.C_ACC)
        c.create_text(CW // 2, 220,
                      text=f"Level {self.lv_mgr.current}: {next_cfg['nama']} — {next_cfg['tema']}",
                      font=("Courier New", 24, "bold"), fill="#a8ff78")
        c.create_text(CW // 2, 280,
                      text="Skor sekarang: " + f"{self.sc_mgr.total:,}",
                      font=("Courier New", 18), fill=self.C_TXT)

        # Tombol atas: lanjut ke level berikutnya (lebar penuh, ditumpuk
        # vertikal supaya teks panjang tidak meluber/tertutup tombol lain)
        bx1, by1, bx2, by2 = CW // 2 - 260, 335, CW // 2 + 260, 395
        btn_rect = c.create_rectangle(bx1, by1, bx2, by2,
                                       fill=self.C_PRI, outline="", tags="btn_next")
        c.create_text((bx1 + bx2) // 2, (by1 + by2) // 2,
                      text="Lanjut ke Level Berikutnya",
                      font=("Courier New", 16, "bold"),
                      fill="#000", tags="btn_next")

        # Tombol bawah: kembali ke menu utama
        mx1, my1, mx2, my2 = CW // 2 - 260, 410, CW // 2 + 260, 470
        btn_menu = c.create_rectangle(mx1, my1, mx2, my2,
                                       fill="#1e4d2b", outline="", tags="btn_menu")
        c.create_text((mx1 + mx2) // 2, (my1 + my2) // 2,
                      text="Kembali ke Menu Utama",
                      font=("Courier New", 16, "bold"),
                      fill=self.C_TXT, tags="btn_menu")

        c.tag_bind("btn_next", "<Button-1>", lambda e: self._start_next())
        c.tag_bind("btn_next", "<Enter>",    lambda e: c.itemconfig(btn_rect, fill=self.C_ACC))
        c.tag_bind("btn_next", "<Leave>",    lambda e: c.itemconfig(btn_rect, fill=self.C_PRI))

        c.tag_bind("btn_menu", "<Button-1>", lambda e: self._back_menu_from_transition())
        c.tag_bind("btn_menu", "<Enter>",    lambda e: c.itemconfig(btn_menu, fill="#2e6d3b"))
        c.tag_bind("btn_menu", "<Leave>",    lambda e: c.itemconfig(btn_menu, fill="#1e4d2b"))

        c.create_text(CW // 2, 505,
                      text="Enter/Space = Lanjut Level Berikutnya",
                      font=("Courier New", 12), fill=self.C_MUT)

        self.bind_all("<Return>", lambda e: self._start_next())
        self.bind_all("<space>",  lambda e: self._start_next())

    def _start_next(self):
        self.unbind_all("<Return>")
        self.unbind_all("<space>")
        self._transition = False
        saved = self.sc_mgr.total
        self._init_level()
        self.sc_mgr.total = saved

    def _back_menu_from_transition(self):
        """Dipanggil saat pemain memilih 'Kembali ke Menu Utama' setelah
        menyelesaikan sebuah level. Progres (level & skor) disimpan agar
        saat pemain memilih main lagi, ia bisa memilih lanjut atau mengulang."""
        self.unbind_all("<Return>")
        self.unbind_all("<space>")
        self._resume_level = self.lv_mgr.current
        self._resume_score = self.sc_mgr.total
        self._transition = False
        self._running    = False
        self._cancel()
        self.controller.show("MenuScreen")

    def _show_resume_choice(self):
        """Layar pilihan yang muncul saat GameScreen dibuka kembali dan ada
        progres level tersimpan: lanjut dari level tersimpan, atau mengulang
        dari Level 1."""
        c = self._cv
        self._hide_hud()
        self._running    = False
        self._transition = True
        self._cancel()

        c.delete("all")
        c.create_rectangle(0, 0, CW, CH, fill="#0a0f1e")
        c.create_text(CW // 2, 150,
                      text="🎮  Lanjutkan Permainan?",
                      font=("Courier New", 34, "bold"), fill=self.C_PRI)
        c.create_text(CW // 2, 215,
                      text=(f"Progres tersimpan: Level {self._resume_level} "
                            f"— Skor {self._resume_score:,}"),
                      font=("Courier New", 18), fill=self.C_TXT)

        bx1, by1, bx2, by2 = CW // 2 - 220, 290, CW // 2 + 220, 345
        btn_resume = c.create_rectangle(bx1, by1, bx2, by2,
                                         fill=self.C_PRI, outline="", tags="btn_resume")
        c.create_text(CW // 2, (by1 + by2) // 2,
                      text=f"▶  Lanjut ke Level {self._resume_level}",
                      font=("Courier New", 16, "bold"),
                      fill="#000", tags="btn_resume")

        rx1, ry1, rx2, ry2 = CW // 2 - 220, 365, CW // 2 + 220, 420
        btn_restart = c.create_rectangle(rx1, ry1, rx2, ry2,
                                          fill=self.C_DNG, outline="", tags="btn_restart")
        c.create_text(CW // 2, (ry1 + ry2) // 2,
                      text="🔄  Ulang dari Level 1",
                      font=("Courier New", 16, "bold"),
                      fill="#fff", tags="btn_restart")

        c.tag_bind("btn_resume", "<Button-1>", lambda e: self._confirm_resume())
        c.tag_bind("btn_resume", "<Enter>",    lambda e: c.itemconfig(btn_resume, fill=self.C_ACC))
        c.tag_bind("btn_resume", "<Leave>",    lambda e: c.itemconfig(btn_resume, fill=self.C_PRI))

        c.tag_bind("btn_restart", "<Button-1>", lambda e: self._confirm_restart())
        c.tag_bind("btn_restart", "<Enter>",    lambda e: c.itemconfig(btn_restart, fill="#ff7a9c"))
        c.tag_bind("btn_restart", "<Leave>",    lambda e: c.itemconfig(btn_restart, fill=self.C_DNG))

    def _confirm_resume(self):
        lvl   = self._resume_level
        score = self._resume_score
        self._resume_level = None
        self._resume_score = 0
        self._transition   = False
        self.lv_mgr.current = lvl
        self._init_level()
        self.sc_mgr.total = score
        self._update_hud()

    def _confirm_restart(self):
        self._resume_level = None
        self._resume_score = 0
        self._transition   = False
        self.lv_mgr.reset()
        self._init_level()

    def _game_end(self, won):
        self._running    = False
        self._transition = False
        self._cancel()
        # Game benar-benar selesai (menang/kalah) -> bersihkan progres
        # tersimpan supaya "Main Lagi" berikutnya mulai dari skor 0 /
        # Level 1, bukan melanjutkan skor game sebelumnya.
        self._resume_level = None
        self._resume_score = 0
        # Leaderboard hanya untuk pemain yang benar-benar menyelesaikan
        # seluruh 3 level (menang). Kalah di tengah jalan tidak dicatat.
        if won:
            self._save_score_checkpoint()
        self.controller.frames["GameOverScreen"].set_result(
            self.sc_mgr.total, self.lv_mgr.current, won)
        self.controller.show("GameOverScreen")

    def _toggle_pause(self):
        if not self._running or self._transition: return
        self._paused = not self._paused
        self._pause_btn.config(text="▶ Lanjut" if self._paused else "⏸ Pause")
        if not self._paused: self._loop()

    def _back_menu(self):
        # Simpan progres (level & skor saat ini) sama seperti saat menekan
        # "Kembali ke Menu Utama" di layar transisi antar-level, supaya saat
        # pemain memilih main lagi, ia ditawari pilihan Lanjut / Ulang alih-
        # alih otomatis kembali ke Level 1.
        self._resume_level = self.lv_mgr.current
        self._resume_score = self.sc_mgr.total
        self._running = False; self._transition = False
        self._cancel()
        self.controller.show("MenuScreen")

    def _cancel(self):
        if self._after:
            self.after_cancel(self._after)
            self._after = None

    def _timer_tick(self):
        if not self._running: return
        if not self._paused and not self._transition:
            if self._timer > 0:
                self._timer -= 1
                self._tm_var.set(f"⏱ {self._timer}")
            else:
                self._level_done(); return
        self.after(1000, self._timer_tick)

    def _update_hud(self):
        cfg = self.lv_mgr.cfg()
        self._lv_var.set(f"Level {self.lv_mgr.current} — {cfg['nama']}")
        self._sc_var.set(f"Skor: {self.sc_mgr.total:,}")
        self._tm_var.set(f"⏱ {self._timer}")
        self._hp_var.set("❤ " * self._lives)

    def _draw(self):
        c    = self._cv
        camx = int(self._cam_x)
        t    = self.lv_mgr.theme()
        f    = self._frame

        c.delete("all")
        c.create_rectangle(0, 0, CW, CH, fill=t["sky"], outline="")

        for i in range(90):
            sx = (i * 137 + 11) % 3600 - camx
            if -2 < sx < CW + 2:
                sy   = (i * 73 + 5) % 260
                twkl = int(128 + 80 * math.sin(f * 0.04 + i))
                col  = f"#{twkl:02x}{twkl:02x}{twkl:02x}"
                c.create_rectangle(sx, sy, sx + 2, sy + 2, fill=col, outline="")

        mx = 80 - int(camx * 0.04)
        my = 20
        c.create_oval(mx, my, mx + 200, my + 200, fill=t["moon"], outline="")
        for cx2, cy2, cr in [(mx+45, my+60, 18), (mx+110, my+85, 12), (mx+75, my+130, 14)]:
            c.create_oval(cx2 - cr, cy2 - cr, cx2 + cr, cy2 + cr, fill="#999", outline="")

        for i in range(7):
            cx2 = (i * 260 - int(camx * (0.08 + i * 0.015))) % (CW + 400) - 150
            cy2 = 280 + i * 14
            c.create_oval(cx2, cy2, cx2 + 220, cy2 + 65, fill="#1d3066", outline="")

        for i in range(0, WORLD_W, 100):
            bx = i - camx
            if -60 < bx < CW + 60:
                th = 70 + (i % 40)
                c.create_rectangle(bx + 14, GROUND_Y - th, bx + 26, GROUND_Y,
                                   fill=t["ground"], outline="")
                c.create_oval(bx - 6, GROUND_Y - th - 24, bx + 46, GROUND_Y - th + 12,
                              fill=t["grass"], outline="")

        for px2, py2, pw, ph in PLATFORMS:
            rx = px2 - camx
            if rx > CW + 20 or rx + pw < -20:
                continue
            c.create_rectangle(rx, py2, rx + pw, py2 + ph, fill=t["platform"], outline="")
            for bx2 in range(0, pw, 22):
                for by2 in range(4, ph, 14):
                    off = (by2 // 14 % 2) * 11
                    c.create_rectangle(rx + bx2 + off, py2 + by2,
                                       rx + bx2 + off + 19, py2 + by2 + 11,
                                       fill=t["ground"], outline="")
            if py2 != GROUND_Y:
                c.create_rectangle(rx, py2, rx + pw, py2 + 8, fill=t["grass"], outline="")
                for gx2 in range(int(rx) + 2, int(rx) + pw, 7):
                    c.create_line(gx2, py2, gx2 + 3, py2 - 7, fill="#5dcc3a", width=2)

        for coin in self._coins:
            if coin.taken: continue
            sx2 = int(coin.x - camx)
            sy2 = int(coin.y)
            if -20 < sx2 < CW + 20:
                if coin.gem:
                    pts = [sx2, sy2-13, sx2+10, sy2, sx2, sy2+13, sx2-10, sy2]
                    c.create_polygon(pts, fill="#4dffb0", outline="#25cc80", width=1)
                else:
                    c.create_oval(sx2-10, sy2-10, sx2+10, sy2+10,
                                  fill="#ffd700", outline="#cc8800", width=2)
                    c.create_text(sx2, sy2, text="$",
                                  font=("Courier New", 10, "bold"), fill="#5a3a00")

        for g in self._ghosts:
            if g.dead: continue
            sx2 = int(g.x - camx)
            if -50 < sx2 < CW + 50:
                _draw_ghost(c, sx2, int(g.y), g.cfg["color"], g.anim, g.hp, g.cfg["hp"])

        for p in self._projs:
            sx2 = int(p.x - camx)
            if -10 < sx2 < CW + 10:
                for i in range(4):
                    s  = max(1, 9 - i * 2)
                    ox = int(-p.vx * i * 0.3)
                    c.create_rectangle(sx2+ox-s//2, int(p.y)-s//2,
                                       sx2+ox+s//2, int(p.y)+s//2,
                                       fill="#8ef", outline="")

        for pt in self._parts:
            for dot in pt.get_dots():
                sx2 = int(dot["x"] - camx)
                if -5 < sx2 < CW + 5:
                    s = max(1, int(dot["size"] * dot["life"] / dot["max"]))
                    c.create_rectangle(sx2-s//2, int(dot["y"])-s//2,
                                       sx2+s//2, int(dot["y"])+s//2,
                                       fill=dot["color"], outline="")

        px = int(self.player.x - camx)
        py = int(self.player.y)
        _draw_player(c, px, py, self.player.W, self.player.H,
                     self.player.on_ground, f)

        cfg = self.lv_mgr.cfg()
        c.create_text(CW - 14, 14,
                      text=f"Level {self.lv_mgr.current}: {cfg['tema']}",
                      anchor="ne", font=("Courier New", 14, "bold"),
                      fill=self.lv_mgr.theme()["label"])

        fin_x = WORLD_W - 120 - camx
        if -10 < fin_x < CW + 10:
            for fy in range(0, CH, 20):
                col = "#fff" if (fy // 20) % 2 == 0 else "#333"
                c.create_rectangle(fin_x, fy, fin_x + 8, fy + 20, fill=col, outline="")
            c.create_text(fin_x + 30, 60, text="FINISH", angle=90,
                          font=("Courier New", 14, "bold"), fill="#fff")