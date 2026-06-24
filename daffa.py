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
                    self.sc_mgr.coin()
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
        bonus = self.sc_mgr.time_bonus(self._timer)

        if self.lv_mgr.is_last():
            self._game_end(won=True)
        else:
            self.lv_mgr.next()
            self._show_transition(bonus)
    
    def _show_transition(self, bonus):
        c       = self._cv
        prev_lv = self.lv_mgr.current - 1
        next_cfg = self.lv_mgr.cfg()

        c.delete("all")
        c.create_rectangle(0, 0, CW, CH, fill="#0a0f1e")
        c.create_text(CW // 2, 150,
                      text=f"✅  Level {prev_lv} Selesai!",
                      font=("Courier New", 36, "bold"), fill=self.C_PRI)
        c.create_text(CW // 2, 230,
                      text=f"Bonus Waktu: +{bonus} poin",
                      font=("Courier New", 24), fill=self.C_ACC)
        c.create_text(CW // 2, 310,
                      text=f"Level {self.lv_mgr.current}: {next_cfg['nama']} — {next_cfg['tema']}",
                      font=("Courier New", 28, "bold"), fill="#a8ff78")
        c.create_text(CW // 2, 400,
                      text="Skor sekarang: " + f"{self.sc_mgr.total:,}",
                      font=("Courier New", 20), fill=self.C_TXT)

        bx1, by1, bx2, by2 = CW // 2 - 160, 455, CW // 2 + 160, 510
        btn_rect = c.create_rectangle(bx1, by1, bx2, by2,
                                       fill=self.C_PRI, outline="", tags="btn_next")
        c.create_text(CW // 2, (by1 + by2) // 2,
                      text="▶  Lanjut ke Level Berikutnya",
                      font=("Courier New", 16, "bold"),
                      fill="#000", tags="btn_next")

        c.tag_bind("btn_next", "<Button-1>", lambda e: self._start_next())
        c.tag_bind("btn_next", "<Enter>",    lambda e: c.itemconfig(btn_rect, fill=self.C_ACC))
        c.tag_bind("btn_next", "<Leave>",    lambda e: c.itemconfig(btn_rect, fill=self.C_PRI))
        self.bind_all("<Return>", lambda e: self._start_next())
        self.bind_all("<space>",  lambda e: self._start_next())

    def _start_next(self):
        self.unbind_all("<Return>")
        self.unbind_all("<space>")
        self._transition = False
        saved = self.sc_mgr.total
        self._init_level()
        self.sc_mgr.total = saved

    def _game_end(self, won):
        self._running    = False
        self._transition = False
        self._cancel()
        user = self.controller.current_user
        if user and user.get("id"):
            try: db_save_score(user["id"], self.sc_mgr.total, self.lv_mgr.current)
            except: pass
        self.controller.frames["GameOverScreen"].set_result(
            self.sc_mgr.total, self.lv_mgr.current, won)
        self.controller.show("GameOverScreen")

    
    