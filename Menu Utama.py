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