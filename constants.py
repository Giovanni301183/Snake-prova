"""
constants.py
Costanti e configurazioni grafiche e di gioco per Snake Game.
"""

# Dimensioni Schermo e Griglia
GRID_SIZE = 25          # Dimensione in pixel di ogni cella della griglia
GRID_WIDTH = 30         # Numero di celle orizzontali (30 * 25 = 750px)
GRID_HEIGHT = 24        # Numero di celle verticali (24 * 25 = 600px)

HEADER_HEIGHT = 70      # Altezza della barra superiore per punteggio e stato
SCREEN_WIDTH = GRID_WIDTH * GRID_SIZE   # 750 px
SCREEN_HEIGHT = (GRID_HEIGHT * GRID_SIZE) + HEADER_HEIGHT  # 670 px

FPS = 60                # Frame rate del rendering grafico

# Velocità di gioco (movimenti per secondo del serpente in base alla difficoltà)
SPEED_CONFIG = {
    "Facile": 8,
    "Medio": 13,
    "Difficile": 18
}

# Punteggi
POINTS_NORMAL_APPLE = 10
POINTS_BONUS_APPLE = 50
BONUS_SPAWN_CHANCE = 0.25   # 25% di probabilità di spawn bonus mela dopo aver mangiato
BONUS_DURATION_SECONDS = 6  # Durata della mela bonus prima di scomparire

# Palette Colori Moderna (Dark Theme con accenti Neon)
COLOR_BG_DARK = (15, 17, 26)           # Sfondo scuro principale (#0F111A)
COLOR_GRID_BG = (22, 27, 39)           # Sfondo area di gioco (#161B27)
COLOR_GRID_LINE = (28, 34, 48)         # Linee sottili della griglia (#1C2230)
COLOR_HEADER_BG = (12, 14, 21)         # Sfondo header HUD

# Serpente (Gradiente verde neon / ciano)
COLOR_SNAKE_HEAD = (0, 255, 170)       # Verde menta brillante
COLOR_SNAKE_BODY_START = (0, 210, 150) # Verde smeraldo
COLOR_SNAKE_BODY_END = (0, 140, 180)   # Gradiente verso turchese
COLOR_SNAKE_EYES = (10, 15, 25)        # Pupille scure
COLOR_SNAKE_EYES_WHITE = (255, 255, 255)

# Cibo
COLOR_FOOD_RED = (255, 65, 84)         # Mela classica rossa
COLOR_FOOD_RED_GLOW = (255, 110, 125)
COLOR_BONUS_GOLD = (255, 204, 0)       # Mela bonus dorata
COLOR_BONUS_GLOW = (255, 235, 120)
COLOR_LEAF = (76, 175, 80)             # Foglia mela

# UI e Testi
COLOR_TEXT_LIGHT = (240, 243, 246)     # Bianco puro/argento
COLOR_TEXT_MUTED = (140, 150, 170)     # Grigio tenue
COLOR_ACCENT = (0, 210, 255)           # Ciano accento
COLOR_GOLD = (255, 215, 0)             # Oro per High Score
COLOR_RED_ALERT = (255, 75, 75)        # Rosso per Game Over
COLOR_PANEL_BG = (24, 30, 44, 220)     # Pannelli trasparenti overlay
COLOR_BUTTON_DEFAULT = (35, 45, 65)
COLOR_BUTTON_HOVER = (50, 70, 100)
COLOR_BUTTON_ACTIVE = (0, 180, 140)
