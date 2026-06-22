leaderboard 

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