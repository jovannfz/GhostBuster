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

    
    
    