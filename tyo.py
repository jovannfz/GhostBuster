import tkinter as tk
from tkinter import messagebox
from jovan  import AuthScreen, db_get_leaderboard, db_get_progress
from ozzy import GameScreen, BaseScreen

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
            self._welcome.config(value=f"Halo, {u['username']}! 👋")

# ══════════════════════════════════════════════════════════════════
#  SCREEN — GAME OVER / VICTORY
# ══════════════════════════════════════════════════════════════════

class GameOverScreen(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self._score   = 0
        self._level   = 1
        self._victory = False
        self._build()

    def _build(self):
        self.columnconfigure(0, weight=1)

        self._icon = tk.Label(self, text="💀", font=("Arial", 80), bg=self.BG)
        self._icon.grid(row=0, column=0, pady=(90, 0))

        self._title = tk.Label(self, text="GAME OVER",
                               font=("Courier New", 44, "bold"),
                               bg=self.BG, fg=self.C_DNG)
        self._title.grid(row=1, column=0, pady=(8, 28))

        card = tk.Frame(self, bg=self.C_CARD, padx=60, pady=32)
        card.grid(row=2, column=0)

        self._sc_var = tk.StringVar(value="Skor Akhir: 0")
        self._lv_var = tk.StringVar(value="Level Tercapai: 1 / 3")

        tk.Label(card, textvariable=self._sc_var,
                 font=("Courier New", 26, "bold"),
                 bg=self.C_CARD, fg=self.C_ACC).pack(pady=4)
        tk.Label(card, textvariable=self._lv_var,
                 font=self.F_HEAD, bg=self.C_CARD, fg=self.C_TXT).pack(pady=4)

        btn = dict(font=self.F_HEAD, width=28, pady=12, relief="flat", cursor="hand2")

        tk.Button(self, text="🔄  MAIN LAGI",    bg=self.C_PRI, fg="#000",
                  command=lambda: self.controller.show("GameScreen"), **btn).grid(
            row=3, column=0, pady=(36, 8))
        tk.Button(self, text="🏆  LEADERBOARD",  bg=self.C_ACC, fg="#000",
                  command=lambda: self.controller.show("LeaderboardScreen"), **btn).grid(
            row=4, column=0, pady=5)
        tk.Button(self, text="🏠  MENU UTAMA",   bg="#1e4d2b", fg=self.C_TXT,
                  command=lambda: self.controller.show("MenuScreen"), **btn).grid(
            row=5, column=0, pady=5)

    def set_result(self, score: int, level: int, victory: bool):
        self._score   = score
        self._level   = level
        self._victory = victory

    def on_show(self):
        if self._victory:
            self._icon.config(text="🏆")
            self._title.config(text="YOU WIN! 🎉", fg=self.C_ACC)
        else:
            self._icon.config(text="💀")
            self._title.config(text="GAME OVER", fg=self.C_DNG)
        self._sc_var.set(f"Skor Akhir: {self._score:,}")
        self._lv_var.set(f"Level Tercapai: {self._level} / 3")

# ══════════════════════════════════════════════════════════════════
#  SCREEN — LEADERBOARD
# ══════════════════════════════════════════════════════════════════

class LeaderboardScreen(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self._build()

    def _build(self):
        self.columnconfigure(0, weight=1)

        tk.Label(self, text="🏆  LEADERBOARD",
                 font=("Courier New", 36, "bold"),
                 bg=self.BG, fg=self.C_ACC).grid(row=0, column=0, pady=(60, 6))
        tk.Label(self, text="Top 10 Ghost Buster Terbaik",
                 font=self.F_BODY, bg=self.BG, fg=self.C_MUT).grid(row=1, column=0, pady=(0, 16))

        tbl  = tk.Frame(self, bg=self.C_CARD)
        tbl.grid(row=2, column=0, padx=80)

        headers = ["#",  "Username", "Skor", "Level", "Tanggal"]
        col_w   = [4,    18,          12,      8,       18]
        for col, (h, w) in enumerate(zip(headers, col_w)):
            tk.Label(tbl, text=h, font=("Courier New", 11, "bold"),
                     bg="#1e3a5c", fg=self.C_ACC, width=w, pady=5).grid(
                row=0, column=col, padx=1, pady=(0, 2), sticky="ew")

        self._rows = []
        for r in range(10):
            row_w = []
            bg = self.C_CARD if r % 2 == 0 else "#0a1528"
            for col, w in enumerate(col_w):
                lbl = tk.Label(tbl, text="—", font=self.F_SM,
                               bg=bg, fg=self.C_TXT, width=w, pady=4)
                lbl.grid(row=r + 1, column=col, padx=1, pady=1, sticky="ew")
                row_w.append(lbl)
            self._rows.append(row_w)

        tk.Button(self, text="🔄  Refresh", font=self.F_BODY,
                  bg="#1e4d2b", fg=self.C_TXT, relief="flat", cursor="hand2",
                  width=14, command=self._load).grid(row=3, column=0, pady=(22, 6))
        tk.Button(self, text="🏠  Kembali ke Menu", font=self.F_BODY,
                  bg=self.C_DNG, fg="#fff", relief="flat", cursor="hand2",
                  width=28, command=lambda: self.controller.show("MenuScreen")).grid(
            row=4, column=0, pady=4) 

    def _load(self):
        try:
            data = db_get_leaderboard(10)
        except Exception:
            data = []

        medals = ["🥇", "🥈", "🥉"] + ["  "] * 7
        for i, widgets in enumerate(self._rows):
            if i < len(data):
                r   = data[i]
                rank = medals[i] if i < 3 else str(i + 1)
                vals = [rank, r["username"], f"{r['score']:,}",
                        str(r["level_reached"]), r["tanggal"]]
                fg = (self.C_ACC if i == 0 else "#c0c0c0" if i == 1 else
                      "#cd7f32" if i == 2 else self.C_TXT)
            else:
                vals = [str(i + 1), "—", "—", "—", "—"]
                fg   = self.C_MUT
            for lbl, val in zip(widgets, vals):
                lbl.config(text=val, fg=fg)

    def on_show(self):
        self._load() 

# ══════════════════════════════════════════════════════════════════
#  SCREEN — PENGATURAN & PROFIL
# ══════════════════════════════════════════════════════════════════

class SettingsScreen(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self._build()

    def _build(self):
        self.columnconfigure(0, weight=1)

        tk.Label(self, text="⚙  PENGATURAN",
                 font=("Courier New", 36, "bold"),
                 bg=self.BG, fg=self.C_PRI).grid(row=0, column=0, pady=(60, 24))

        card = tk.Frame(self, bg=self.C_CARD, padx=70, pady=32)
        card.grid(row=1, column=0, pady=8)
        card.columnconfigure(1, weight=1) 

        tk.Label(card, text="👤  Profil Pemain",
                 font=self.F_HEAD, bg=self.C_CARD, fg=self.C_ACC).grid(
            row=0, column=0, columnspan=2, pady=(0, 14), sticky="w")

        self._uname_lbl = tk.Label(card, text="Username: —",
                                   font=self.F_BODY, bg=self.C_CARD, fg=self.C_TXT)
        self._uname_lbl.grid(row=1, column=0, columnspan=2, sticky="w", pady=3)

        self._best_lbl = tk.Label(card, text="Skor Terbaik: —",
                                  font=self.F_BODY, bg=self.C_CARD, fg=self.C_TXT)
        self._best_lbl.grid(row=2, column=0, columnspan=2, sticky="w", pady=3)

        self._lv_lbl = tk.Label(card, text="Level Tertinggi: —",
                                font=self.F_BODY, bg=self.C_CARD, fg=self.C_TXT)
        self._lv_lbl.grid(row=3, column=0, columnspan=2, sticky="w", pady=3)

        card2 = tk.Frame(self, bg=self.C_CARD, padx=70, pady=30)
        card2.grid(row=2, column=0, pady=8) 

        tk.Label(card2, text="🎮  Kontrol",
                 font=self.F_HEAD, bg=self.C_CARD, fg=self.C_ACC).grid(
            row=0, column=0, columnspan=2, pady=(0, 12), sticky="w")

        controls = [
            ("Gerak",   "← → / A D"),
            ("Lompat",  "SPACE / ↑ / W"),
            ("Tembak",  "Z  atau  X"),
            ("Pause",   "Tombol Pause di layar"),
            ("Kembali", "Tombol Menu di layar"),
        ]
        for i, (act, key) in enumerate(controls):
            tk.Label(card2, text=f"{act}:", font=self.F_BODY,
                     bg=self.C_CARD, fg=self.C_MUT, width=12, anchor="w").grid(
                row=i + 1, column=0, sticky="w", pady=2)
            tk.Label(card2, text=key, font=("Courier New", 12, "bold"),
                     bg=self.C_CARD, fg=self.C_PRI).grid(
                row=i + 1, column=1, sticky="w", padx=(14, 0), pady=2)

        tk.Button(self, text="🚪  Logout", font=self.F_HEAD, width=26, pady=12,
                  bg=self.C_DNG, fg="#fff", relief="flat", cursor="hand2",
                  command=self._logout).grid(row=3, column=0, pady=(30, 8))
        tk.Button(self, text="🏠  Kembali ke Menu", font=self.F_BODY,
                  width=26, pady=10, bg="#1e4d2b", fg=self.C_TXT,
                  relief="flat", cursor="hand2",
                  command=lambda: self.controller.show("MenuScreen")).grid(
            row=4, column=0, pady=4)
    
    def on_show(self):
        u = self.controller.current_user
        if not u: return
        self._uname_lbl.config(text=f"Username: {u['username']}")
        try:
            prog = db_get_progress(u["id"])
            if prog:
                self._best_lbl.config(text=f"Skor Terbaik: {prog['skor_terbaik']:,}")
                names = {1: "Easy", 2: "Medium", 3: "Hard"}
                lv = prog["level_tercapai"]
                self._lv_lbl.config(text=f"Level Tertinggi: {lv} — {names.get(lv, '?')}")
            else:
                self._best_lbl.config(text="Skor Terbaik: 0")
                self._lv_lbl.config(text="Level Tertinggi: 1 — Easy")
        except Exception:
            self._best_lbl.config(text="Skor Terbaik: (DB tidak konek)")
            self._lv_lbl.config(text="—")

    def _logout(self):
        self.controller.set_user(None)
        self.controller.show("AuthScreen") 

# ══════════════════════════════════════════════════════════════════
#  APP CONTROLLER — ENTRY POINT
# ══════════════════════════════════════════════════════════════════

class App(tk.Tk):
    WIDTH  = 1366
    HEIGHT = 768

    def __init__(self):
        super().__init__()
        self.title("GhostBusters 👻")
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}+0+0")
        self.resizable(False, False)
        self.configure(bg="#0a0f1e")

        self.current_user = None

        container = tk.Frame(self, bg="#0a0f1e")
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for Cls in [AuthScreen, MenuScreen, GameScreen,
                    GameOverScreen, LeaderboardScreen, SettingsScreen]:
            name = Cls.__name__
            f    = Cls(parent=container, controller=self)
            self.frames[name] = f
            f.grid(row=0, column=0, sticky="nsew")

        self.show("AuthScreen")
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def show(self, name: str):
        frame = self.frames[name]
        frame.tkraise()
        frame.on_show()

    def set_user(self, user):
        self.current_user = user

    def _on_close(self):
        if messagebox.askokcancel("Keluar", "Yakin ingin keluar dari GhostBusters?"):
            self.destroy()

    def quit(self):
        self._on_close()

# ══════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    try:
        App().mainloop()
    except Exception as e:
        import traceback; traceback.print_exc()
        try:
            messagebox.showerror("Error Fatal",
                f"Gagal menjalankan aplikasi:\n\n{e}\n\n"
                "Pastikan MySQL sudah berjalan dan konfigurasi\n"
                "DB_CONFIG di bagian atas file sudah benar.")
        except Exception:
            pass  