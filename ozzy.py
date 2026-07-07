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