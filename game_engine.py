"""
game_engine.py
Logica centrale di gioco, gestione del serpente, cibo, particelle e record.
"""

import os
import json
import random
import time
from datetime import datetime
from constants import (
    GRID_WIDTH, GRID_HEIGHT, SPEED_CONFIG,
    POINTS_NORMAL_APPLE, POINTS_BONUS_APPLE,
    BONUS_SPAWN_CHANCE, BONUS_DURATION_SECONDS,
    COLOR_FOOD_RED, COLOR_BONUS_GOLD, COLOR_SNAKE_HEAD
)

# Direzioni (dx, dy)
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

OPPOSITES = {
    UP: DOWN,
    DOWN: UP,
    LEFT: RIGHT,
    RIGHT: LEFT
}

class Particle:
    """Particella visiva per effetti di esplosione quando si mangia."""
    def __init__(self, x: float, y: float, color: tuple):
        self.x = x
        self.y = y
        self.color = color
        angle = random.uniform(0, 2 * 3.14159)
        speed = random.uniform(50, 180)
        self.vx = speed * random.random() * (1 if random.random() > 0.5 else -1)
        self.vy = speed * random.random() * (1 if random.random() > 0.5 else -1)
        self.lifetime = random.uniform(0.3, 0.6)
        self.max_lifetime = self.lifetime
        self.radius = random.uniform(2, 5)

    def update(self, dt: float) -> bool:
        """Aggiorna la posizione e durata. Ritorna False se è scaduta."""
        self.lifetime -= dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.radius = max(0.5, self.radius * (self.lifetime / self.max_lifetime))
        return self.lifetime > 0

class ScoreManager:
    """Gestisce il salvataggio e caricamento dei punteggi massimi."""
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.high_score = self.load_high_score()

    def load_high_score(self) -> int:
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("high_score", 0)
            except Exception:
                return 0
        return 0

    def save_high_score(self, score: int) -> bool:
        """Salva il nuovo record se superiore al precedente. Ritorna True se nuovo record."""
        if score > self.high_score:
            self.high_score = score
            data = {
                "high_score": score,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            try:
                with open(self.filepath, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4)
                return True
            except Exception as e:
                print(f"Errore salvataggio punteggio: {e}")
        return False

class GameEngine:
    """Motore del gioco Snake."""
    def __init__(self, score_filepath: str):
        self.score_manager = ScoreManager(score_filepath)
        self.high_score = self.score_manager.high_score
        
        # Impostazioni configurabili
        self.difficulty = "Medio"
        self.wrap_around = False  # False = Muri mortali; True = Teletrasporto
        self.sound_enabled = True

        # Callback per eventi audio
        self.on_eat_sound = None
        self.on_bonus_sound = None
        self.on_game_over_sound = None

        # Particelle grafiche
        self.particles: list[Particle] = []

        # Stato di gioco
        self.state = "MENU"  # "MENU", "PLAYING", "PAUSED", "GAME_OVER"
        self.is_new_high_score = False

        self.reset_game()

    def reset_game(self):
        """Inizializza una nuova partita."""
        center_x = GRID_WIDTH // 2
        center_y = GRID_HEIGHT // 2

        # Serpente: testa al centro, corpo verso sinistra
        self.snake = [
            (center_x, center_y),
            (center_x - 1, center_y),
            (center_x - 2, center_y)
        ]
        self.direction = RIGHT
        self.next_direction = RIGHT
        
        self.score = 0
        self.is_new_high_score = False
        self.apples_eaten = 0
        self.bonus_food = None
        self.bonus_timer = 0.0

        self.move_timer = 0.0
        self.particles.clear()
        
        self.food = self._spawn_food()

    @property
    def speed(self) -> int:
        return SPEED_CONFIG.get(self.difficulty, 13)

    def _spawn_food(self) -> tuple[int, int]:
        """Trova una posizione casuale libera per la mela."""
        occupied = set(self.snake)
        if self.bonus_food:
            occupied.add(self.bonus_food)

        available_cells = [
            (x, y) for x in range(GRID_WIDTH) for y in range(GRID_HEIGHT)
            if (x, y) not in occupied
        ]
        if not available_cells:
            return (0, 0)
        return random.choice(available_cells)

    def _spawn_bonus_food(self):
        """Spawna una mela dorata bonus a tempo."""
        occupied = set(self.snake)
        occupied.add(self.food)

        available_cells = [
            (x, y) for x in range(GRID_WIDTH) for y in range(GRID_HEIGHT)
            if (x, y) not in occupied
        ]
        if available_cells:
            self.bonus_food = random.choice(available_cells)
            self.bonus_timer = BONUS_DURATION_SECONDS

    def change_direction(self, new_dir: tuple[int, int]):
        """Modifica la direzione evitando inversioni a 180° nello stesso frame."""
        if self.state != "PLAYING":
            return
        if new_dir != OPPOSITES.get(self.direction):
            self.next_direction = new_dir

    def toggle_pause(self):
        """Mette in pausa o riprende la partita."""
        if self.state == "PLAYING":
            self.state = "PAUSED"
        elif self.state == "PAUSED":
            self.state = "PLAYING"

    def add_particles_at(self, gx: int, gy: int, color: tuple, count: int = 15):
        """Crea un'esplosione di particelle in una cella."""
        from constants import GRID_SIZE, HEADER_HEIGHT
        px = gx * GRID_SIZE + GRID_SIZE // 2
        py = gy * GRID_SIZE + HEADER_HEIGHT + GRID_SIZE // 2
        for _ in range(count):
            self.particles.append(Particle(px, py, color))

    def update(self, dt: float):
        """Aggiorna lo stato del gioco con delta time in secondi."""
        # Aggiorna particelle sempre, anche a fine partita
        self.particles = [p for p in self.particles if p.update(dt)]

        if self.state != "PLAYING":
            return

        # Aggiorna timer bonus mela
        if self.bonus_food:
            self.bonus_timer -= dt
            if self.bonus_timer <= 0:
                self.bonus_food = None
                self.bonus_timer = 0.0

        # Aggiorna movimento del serpente a frequenza fissa
        self.move_timer += dt
        move_interval = 1.0 / self.speed

        if self.move_timer >= move_interval:
            self.move_timer -= move_interval
            self._move_snake()

    def _move_snake(self):
        """Esegue un passo di movimento del serpente."""
        self.direction = self.next_direction
        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)

        # Gestione teletrasporto o collisione coi bordi
        if self.wrap_around:
            new_head = (new_head[0] % GRID_WIDTH, new_head[1] % GRID_HEIGHT)
        else:
            if new_head[0] < 0 or new_head[0] >= GRID_WIDTH or new_head[1] < 0 or new_head[1] >= GRID_HEIGHT:
                self._trigger_game_over()
                return

        # Collisione con il proprio corpo
        if new_head in self.snake:
            self._trigger_game_over()
            return

        # Movimento normale
        self.snake.insert(0, new_head)

        # Controllo se ha mangiato la mela normale
        if new_head == self.food:
            self.score += POINTS_NORMAL_APPLE
            self.apples_eaten += 1
            self.add_particles_at(new_head[0], new_head[1], COLOR_FOOD_RED, count=16)
            
            if self.sound_enabled and self.on_eat_sound:
                self.on_eat_sound()

            self.food = self._spawn_food()

            # Possibilità di spawn bonus
            if not self.bonus_food and random.random() < BONUS_SPAWN_CHANCE:
                self._spawn_bonus_food()

        # Controllo se ha mangiato la mela bonus
        elif self.bonus_food and new_head == self.bonus_food:
            self.score += POINTS_BONUS_APPLE
            self.add_particles_at(new_head[0], new_head[1], COLOR_BONUS_GOLD, count=25)
            
            if self.sound_enabled and self.on_bonus_sound:
                self.on_bonus_sound()

            self.bonus_food = None
            self.bonus_timer = 0.0

        else:
            # Non ha mangiato nulla, rimuove la coda
            self.snake.pop()

        # Verifica aggiornamento record durante il gioco
        if self.score > self.high_score:
            self.high_score = self.score
            self.is_new_high_score = True

    def _trigger_game_over(self):
        """Gestisce la conclusione della partita."""
        self.state = "GAME_OVER"
        saved = self.score_manager.save_high_score(self.score)
        if saved:
            self.is_new_high_score = True
            self.high_score = self.score
            
        if self.sound_enabled and self.on_game_over_sound:
            self.on_game_over_sound()
