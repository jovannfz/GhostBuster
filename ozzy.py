# ══════════════════════════════════════════════════════════════════
#  OZY — GAME SCREEN (RENDERING & GAME LOOP)
#  Berisi: data dunia (PLATFORMS, COIN_POS, GHOST_POS),
#          fungsi draw (_draw_ghost, _draw_player),
#          dan GameScreen lengkap (loop, update, draw, HUD)
# ══════════════════════════════════════════════════════════════════

import tkinter as tk
import math

# Import dari file teman-teman
from tyo_game_logic import (
    LevelManager, ScoreManager, PlayerPhysics,
    GhostAI, CoinItem, Projectile, Particle,
    _rect_collide, GROUND_Y, P_FLOOR
)
from jovan_db_auth import db_save_score


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
    (280, 345, False), (400, 300, False), (560, 295, True),  (700, 250, False),
    (840, 245, False), (960, 310, True),  (1100, 305, False),(1300, 235, False),
    (1450, 235, True), (1620, 275, False),(1760, 275, False),(1900, 195, True),
    (2060, 195, False),(2200, 195, False),(2430, 165, True), (2580, 165, False),
    (2720, 235, False),(2860, 235, True), (3000, 155, False),(3160, 225, False),
    (3300, 225, True), (3440, 145, False),
]

GHOST_POS = [
    (420, 300, 0), (680, 250, 1), (900, 250, 0), (1180, 240, 2),
    (1380, 240, 0),(1700, 200, 1),(1960, 260, 0),(2240, 170, 2),
    (2500, 240, 0),(2760, 240, 1),(3020, 160, 0),(3260, 230, 2),
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