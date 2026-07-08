import math
import random



LEVEL_CFG = {
    1: {"nama": "Easy",   "tema": "Hutan Siang",   "kecepatan": 2.5, "timer": 120, "hantu": 5,  "mult": 1.0},
    2: {"nama": "Medium", "tema": "Kuburan Malam", "kecepatan": 4.0, "timer": 80,  "hantu": 9,  "mult": 1.5},
    3: {"nama": "Hard",   "tema": "Kastil Iblis",  "kecepatan": 6.5, "timer": 50,  "hantu": 14, "mult": 2.0},
}

THEME = {
    1: {"sky": "#1a3a6c", "ground": "#2d5a1b", "platform": "#5a3a1a", "grass": "#3a8a2a", "label": "#a8ff78", "moon": "#c8c8c8"},
    2: {"sky": "#0d1a2e", "ground": "#1a1a2e", "platform": "#3a2a0a", "grass": "#1a3a1a", "label": "#f9d423", "moon": "#888899"},
    3: {"sky": "#0a0a1e", "ground": "#1a0a0a", "platform": "#2a0a0a", "grass": "#3a0a0a", "label": "#ff416c", "moon": "#665566"},
}

GHOST_TYPES = [
    {"color": "#e8e8f0", "speed_mult": 1.0, "hp": 1, "score": 100, "name": "Normal"},
    {"color": "#f8c0d8", "speed_mult": 1.6, "hp": 1, "score": 80,  "name": "Cepat"},
    {"color": "#c0b0f0", "speed_mult": 0.6, "hp": 3, "score": 200, "name": "Kuat"},
]

GROUND_Y = 460   
P_FLOOR  = 426   



class LevelManager:
    def __init__(self):
        self.current = 1
        self.max     = 3

    def cfg(self):     return LEVEL_CFG[self.current]
    def theme(self):   return THEME[self.current]
    def is_last(self): return self.current == self.max
    def reset(self):   self.current = 1

    def next(self) -> bool:
        if self.current < self.max:
            self.current += 1
            return True
        return False



class ScoreManager:
    BASE_COIN = 50
    TIME_MULT = 5

    def __init__(self, mult=1.0):
        self.mult  = mult
        self.total = 0

    def ghost_kill(self, base=100):
        g = int(base * self.mult); self.total += g; return g

    def coin(self):
        # Nilai koin dibuat flat (tidak dikali mult level), supaya di semua
        # level 1 koin = +1 skor (bukan 50/75/100 sesuai mult level).
        g = 1; self.total += g; return g

    def time_bonus(self, secs):
        b = int(secs * self.TIME_MULT * self.mult); self.total += b; return b

    def penalty(self, amt=50):
        self.total = max(0, self.total - amt)



class PlayerPhysics:
    GRAVITY  = 0.55
    JUMP_POW = -13.0
    W, H     = 26, 34

    def __init__(self):
        self.GROUND_Y   = P_FLOOR
        self.x          = 80.0
        self.y          = float(P_FLOOR)
        self.vx         = 0.0
        self.vy         = 0.0
        self.on_ground  = True
        self._jump_held = False
        self.platforms  = []

    def jump(self, held: bool):
        if held and self.on_ground and not self._jump_held:
            self.vy = self.JUMP_POW
            self.on_ground = False
            self._jump_held = True
        if not held:
            self._jump_held = False

    def move(self, direction: int, speed: float = 3.5):
        self.vx = direction * speed if direction != 0 else self.vx * 0.65

    def update(self):
        self.vy = min(self.vy + self.GRAVITY, 18)

        prev_x = self.x
        prev_y = self.y

        # --- Gerak & tabrakan horizontal (nabrak sisi platform) ---
        self.x += self.vx
        self._collide_x(prev_x)

        # --- Gerak & tabrakan vertikal (lompat dari bawah / mendarat di atas) ---
        self.y += self.vy
        self.on_ground = False
        self._collide_y(prev_y)

        if self.y >= self.GROUND_Y:
            self.y = float(self.GROUND_Y)
            self.vy = 0
            self.on_ground = True

    def _collide_x(self, prev_x):
        """Blokir gerak horizontal saat menabrak sisi kiri/kanan platform,
        supaya tidak bisa tembus saat 'ditabrak' dari samping."""
        for px1, py1, px2, py2 in self.platforms:
            if px2 - px1 > 1000:
                continue  # lantai utama (sangat lebar), sudah ditangani lewat GROUND_Y
            if self.y + self.H <= py1 or self.y >= py2:
                continue  # tidak ada overlap vertikal dengan platform ini

            if self.vx > 0 and prev_x + self.W <= px1 and self.x + self.W > px1:
                self.x  = px1 - self.W
                self.vx = 0
            elif self.vx < 0 and prev_x >= px2 and self.x < px2:
                self.x  = px2
                self.vx = 0

    def _collide_y(self, prev_y):
        """Mendarat di atas platform (diinjak) saat jatuh, dan mentok/berhenti
        saat melompat dari bawah mengenai bagian bawah platform (tidak tembus)."""
        for px1, py1, px2, py2 in self.platforms:
            if px2 - px1 > 1000:
                continue  # lantai utama (sangat lebar), sudah ditangani lewat GROUND_Y
            if self.x + self.W <= px1 or self.x >= px2:
                continue  # tidak ada overlap horizontal dengan platform ini

            if self.vy >= 0 and prev_y + self.H <= py1 and self.y + self.H > py1:
                # jatuh & mendarat di atas platform -> jadi pijakan
                self.y  = py1 - self.H
                self.vy = 0
                self.on_ground = True
            elif self.vy < 0 and prev_y >= py2 and self.y < py2:
                # lompat dari bawah kena bagian bawah platform -> mentok, tidak tembus
                self.y  = py2
                self.vy = 0

    def rect(self):
        return (self.x, self.y, self.x + self.W, self.y + self.H)

    def collides(self, ox, oy, ow, oh):
        x1, y1, x2, y2 = self.rect()
        return x1 < ox + ow and x2 > ox and y1 < oy + oh and y2 > oy



class GhostAI:
    def __init__(self, x, y, speed, gtype=0):
        self.x      = float(x)
        self.y      = float(y)
        self.base_y = float(y)
        self.cfg    = GHOST_TYPES[gtype % len(GHOST_TYPES)]
        self.hp     = self.cfg["hp"]
        self.speed  = speed * self.cfg["speed_mult"]
        self.vx     = self.speed * random.choice([-1, 1])
        self.anim   = random.uniform(0, math.pi * 2)
        self.dead   = False

    def update(self, player_x):
        if self.dead: return
        self.anim += 0.055
        self.y = self.base_y + math.sin(self.anim) * 14
        dx = player_x - self.x
        if abs(dx) < 450:
            self.vx += math.copysign(0.05, dx)
            top = self.speed * 1.4
            self.vx = max(-top, min(top, self.vx))
        self.x += self.vx

    def hit(self):
        self.hp -= 1
        if self.hp <= 0: self.dead = True

    def rect(self):
        return (self.x - 14, self.y - 20, 28, 36)



class CoinItem:
    def __init__(self, x, y, gem=False):
        self.x      = float(x)
        self.y      = float(y)
        self.base_y = float(y)
        self.gem    = gem
        self.taken  = False
        self.anim   = random.uniform(0, math.pi * 2)

    def update(self):
        self.anim += 0.07
        self.y = self.base_y + math.sin(self.anim) * 4

    def rect(self):
        return (self.x - 9, self.y - 9, 18, 18)



class Projectile:
    def __init__(self, x, y, direction):
        self.x    = float(x)
        self.y    = float(y)
        self.vx   = direction * 11.0
        self.life = 38

    def update(self):
        self.x += self.vx
        self.life -= 1

    def rect(self):
        return (self.x - 6, self.y - 6, 12, 12)



class Particle:
    def __init__(self, x, y, color, count=10, speed=3):
        self.items = []
        for _ in range(count):
            a = random.uniform(0, math.pi * 2)
            s = random.uniform(1, speed)
            l = random.randint(15, 28)
            self.items.append({
                "x": x, "y": y,
                "vx": math.cos(a) * s, "vy": math.sin(a) * s - 1,
                "life": l, "max": l,
                "size": random.randint(2, 5),
                "color": color
            })

    def update(self):
        for p in self.items:
            p["x"] += p["vx"]; p["y"] += p["vy"]
            p["vy"] += 0.12;   p["life"] -= 1

    def alive(self):
        return any(p["life"] > 0 for p in self.items)

    def get_dots(self):
        return [p for p in self.items if p["life"] > 0]



def _rect_collide(a, b):
    return (a[0] < b[0] + b[2] and a[0] + a[2] > b[0] and
            a[1] < b[1] + b[3] and a[1] + a[3] > b[1])