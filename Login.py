import tkinter as tk


class AuthScreen(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self._mode = "login"
        self._build()

    def _build(self):
        self.columnconfigure(0, weight=1)

        tk.Label(self, text="👻  GHOSTBUSTERS  👻",
                 font=("Courier New", 30, "bold"),
                 bg=self.BG, fg=self.C_PRI).grid(row=0, column=0, pady=(80,6))
        tk.Label(self, text="Bust ghosts. Save the night.",
                 font=("Courier New", 16), bg=self.BG, fg=self.C_MUT).grid(row=1, column=0, pady=(0,28))

        card = tk.Frame(self, bg=self.C_CARD, padx=70, pady=44)
        card.grid(row=2, column=0)

        self._title = tk.Label(card, text="LOGIN",
                               font=("Courier New", 22, "bold"),
                               bg=self.C_CARD, fg=self.C_ACC)
        self._title.grid(row=0, column=0, columnspan=2, pady=(0,18))

        for lbl, row in [("Username", 1), ("Password", 3)]:
            tk.Label(card, text=lbl, font=self.F_BODY,
                     bg=self.C_CARD, fg=self.C_TXT).grid(
                row=row, column=0, sticky="w", pady=3)

        entry_cfg = dict(font=self.F_BODY, width=32, bg="#060f1a",
                         fg=self.C_TXT, insertbackground="white",
                         relief="flat", highlightthickness=1,
                         highlightbackground=self.C_PRI)

        self._user_var = tk.StringVar()
        self._pw_var   = tk.StringVar()
        self._cf_var   = tk.StringVar()

        tk.Entry(card, textvariable=self._user_var, **entry_cfg).grid(
            row=2, column=0, columnspan=2, ipady=6, pady=(0,8))
        self._pw_entry = tk.Entry(card, textvariable=self._pw_var, show="•", **entry_cfg)
        self._pw_entry.grid(row=4, column=0, columnspan=2, ipady=6, pady=(0,8))

        self._cf_lbl = tk.Label(card, text="Konfirmasi Password",
                                font=self.F_BODY, bg=self.C_CARD, fg=self.C_TXT)
        self._cf_entry = tk.Entry(card, textvariable=self._cf_var, show="•", **entry_cfg)

        self._btn = tk.Button(card, text="MASUK",
                              font=self.F_HEAD, bg=self.C_PRI, fg="#000",
                              relief="flat", cursor="hand2", width=28, pady=10,
                              command=self._action)
        self._btn.grid(row=7, column=0, columnspan=2, pady=(14,8))

        self._toggle = tk.Label(card, text="Belum punya akun? Daftar di sini",
                                font=self.F_SM, bg=self.C_CARD,
                                fg=self.C_ACC, cursor="hand2")
        self._toggle.grid(row=8, column=0, columnspan=2)
        self._toggle.bind("<Button-1>", lambda e: self._switch())

        self._msg = tk.StringVar()
        tk.Label(self, textvariable=self._msg, font=self.F_SM,
                 bg=self.BG, fg=self.C_DNG, wraplength=400).grid(row=3, column=0, pady=(8,0))

    def _switch(self):
        self._msg.set("")
        if self._mode == "login":
            self._mode = "register"
            self._title.config(text="REGISTER")
            self._btn.config(text="DAFTAR")
            self._toggle.config(text="Sudah punya akun? Login di sini")
            self._cf_lbl.grid(row=5, column=0, sticky="w", pady=3)
            self._cf_entry.grid(row=6, column=0, columnspan=2, ipady=6, pady=(0,8))
        else:
            self._mode = "login"
            self._title.config(text="LOGIN")
            self._btn.config(text="MASUK")
            self._toggle.config(text="Belum punya akun? Daftar di sini")
            self._cf_lbl.grid_remove()
            self._cf_entry.grid_remove()

    def _action(self):
        u = self._user_var.get().strip()
        p = self._pw_var.get().strip()
        if not u or not p:
            self._msg.set("⚠ Username & password wajib diisi."); return

        if self._mode == "register":
            c = self._cf_var.get().strip()
            if p != c:
                self._msg.set("⚠ Password tidak cocok."); return
            res = register_user(u, p)
        else:
            res = login_user(u, p)

        if res["success"]:
            self._msg.set("")
            user = res.get("user") or {"id": None, "username": u}
            self.controller.set_user(user)
            self.controller.show("MenuScreen")
        else:
            self._msg.set(f"⚠ {res['message']}")

    def on_show(self):
        self._user_var.set(""); self._pw_var.set(""); self._cf_var.set("")
        self._msg.set("")
        if self._mode != "login": self._switch()
