"""
snake_tkinter.py
Versione Standalone di Snake realizzata con Tkinter (Standard Library Python).
Non richiede l'installazione di librerie esterne (Zero Dipendenze).
Funziona immediatamente su qualsiasi installazione Python standard.
"""

import tkinter as tk
from tkinter import messagebox
import random
import json
import os

GRID_SIZE = 22
GRID_WIDTH = 28
GRID_HEIGHT = 22
CANVAS_WIDTH = GRID_WIDTH * GRID_SIZE
CANVAS_HEIGHT = GRID_HEIGHT * GRID_SIZE

SPEED_MAP = {
    "Facile": 120,   # ms di ritardo (più alto = più lento)
    "Medio": 80,
    "Difficile": 50
}

class SnakeTkinterApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Snake Game (Tkinter Edition - Zero Dipendenze)")
        self.root.resizable(False, False)
        self.root.configure(bg="#0f111a")

        self.scores_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scores.json")
        self.high_score = self._load_high_score()

        self.difficulty_var = tk.StringVar(value="Medio")
        self.wrap_var = tk.BooleanVar(value=False)

        self.score = 0
        self.snake = []
        self.direction = "Right"
        self.next_direction = "Right"
        self.food = (0, 0)
        self.bonus_food = None
        self.bonus_timer = 0
        self.game_running = False
        self.is_paused = False
        self.loop_id = None

        self._build_ui()
        self.reset_game()

    def _load_high_score(self) -> int:
        if os.path.exists(self.scores_file):
            try:
                with open(self.scores_file, "r", encoding="utf-8") as f:
                    return json.load(f).get("high_score", 0)
            except Exception:
                pass
        return 0

    def _save_high_score(self, score: int):
        if score > self.high_score:
            self.high_score = score
            self.lbl_high_score.config(text=f"Record: {self.high_score}")
            try:
                with open(self.scores_file, "w", encoding="utf-8") as f:
                    json.dump({"high_score": score}, f, indent=4)
            except Exception:
                pass

    def _build_ui(self):
        # Header / Barra superiore
        header = tk.Frame(self.root, bg="#161b27", padx=15, pady=10)
        header.pack(fill=tk.X)

        self.lbl_score = tk.Label(header, text="Punteggio: 0", font=("Segoe UI", 13, "bold"), fg="#00ffaa", bg="#161b27")
        self.lbl_score.pack(side=tk.LEFT, padx=10)

        self.lbl_high_score = tk.Label(header, text=f"Record: {self.high_score}", font=("Segoe UI", 13, "bold"), fg="#ffd700", bg="#161b27")
        self.lbl_high_score.pack(side=tk.LEFT, padx=20)

        # Controlli difficoltà
        tk.Label(header, text="Difficoltà:", font=("Segoe UI", 10), fg="#8c96aa", bg="#161b27").pack(side=tk.LEFT, padx=(20, 5))
        diff_menu = tk.OptionMenu(header, self.difficulty_var, "Facile", "Medio", "Difficile", command=self._on_diff_change)
        diff_menu.config(bg="#232d41", fg="#ffffff", activebackground="#00b48c", highlightthickness=0, font=("Segoe UI", 9))
        diff_menu["menu"].config(bg="#232d41", fg="#ffffff")
        diff_menu.pack(side=tk.LEFT)

        # Checkbox teletrasporto
        chk_wrap = tk.Checkbutton(header, text="Teletrasporto bordi", variable=self.wrap_var, font=("Segoe UI", 10), fg="#00d2ff", bg="#161b27", selectcolor="#0f111a", activebackground="#161b27", activeforeground="#00d2ff")
        chk_wrap.pack(side=tk.LEFT, padx=15)

        # Area Canvas di Gioco
        self.canvas = tk.Canvas(self.root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="#121620", highlightthickness=2, highlightbackground="#232d41")
        self.canvas.pack(padx=12, pady=10)

        # Barra inferiore per comandi
        footer = tk.Frame(self.root, bg="#0f111a", pady=8)
        footer.pack(fill=tk.X)

        btn_restart = tk.Button(footer, text="🔄 Nuova Partita (Spazio)", font=("Segoe UI", 10, "bold"), bg="#00b48c", fg="#ffffff", activebackground="#00ffaa", relief=tk.FLAT, padx=12, pady=4, command=self.start_game)
        btn_restart.pack(side=tk.LEFT, padx=15)

        btn_pause = tk.Button(footer, text="⏸ Pausa (P)", font=("Segoe UI", 10), bg="#232d41", fg="#ffffff", activebackground="#324664", relief=tk.FLAT, padx=10, pady=4, command=self.toggle_pause)
        btn_pause.pack(side=tk.LEFT, padx=5)

        lbl_hint = tk.Label(footer, text="Comandi: Frecce o W A S D | P: Pausa", font=("Segoe UI", 9), fg="#8c96aa", bg="#0f111a")
        lbl_hint.pack(side=tk.RIGHT, padx=15)

        # Bind tasti da tastiera
        self.root.bind("<Up>", lambda e: self._change_direction("Up"))
        self.root.bind("<Down>", lambda e: self._change_direction("Down"))
        self.root.bind("<Left>", lambda e: self._change_direction("Left"))
        self.root.bind("<Right>", lambda e: self._change_direction("Right"))
        self.root.bind("<w>", lambda e: self._change_direction("Up"))
        self.root.bind("<s>", lambda e: self._change_direction("Down"))
        self.root.bind("<a>", lambda e: self._change_direction("Left"))
        self.root.bind("<d>", lambda e: self._change_direction("Right"))
        self.root.bind("<W>", lambda e: self._change_direction("Up"))
        self.root.bind("<S>", lambda e: self._change_direction("Down"))
        self.root.bind("<A>", lambda e: self._change_direction("Left"))
        self.root.bind("<D>", lambda e: self._change_direction("Right"))
        self.root.bind("<space>", lambda e: self._handle_space())
        self.root.bind("<p>", lambda e: self.toggle_pause())
        self.root.bind("<P>", lambda e: self.toggle_pause())

    def _on_diff_change(self, val):
        self.canvas.focus_set()

    def _handle_space(self):
        if not self.game_running:
            self.start_game()
        else:
            self.toggle_pause()

    def _change_direction(self, new_dir: str):
        opposites = {"Up": "Down", "Down": "Up", "Left": "Right", "Right": "Left"}
        if opposites.get(self.direction) != new_dir:
            self.next_direction = new_dir

    def toggle_pause(self):
        if not self.game_running:
            return
        self.is_paused = not self.is_paused
        if not self.is_paused:
            self._game_loop()
        else:
            self.canvas.create_text(CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2, text="⏸ IN PAUSA", font=("Segoe UI", 24, "bold"), fill="#00d2ff", tag="pause_text")

    def reset_game(self):
        if self.loop_id:
            self.root.after_cancel(self.loop_id)
            self.loop_id = None

        cx, cy = GRID_WIDTH // 2, GRID_HEIGHT // 2
        self.snake = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
        self.direction = "Right"
        self.next_direction = "Right"
        self.score = 0
        self.bonus_food = None
        self.bonus_timer = 0
        self.is_paused = False
        self.lbl_score.config(text=f"Punteggio: {self.score}")
        self.food = self._spawn_food()
        self._draw_board()

    def start_game(self):
        self.reset_game()
        self.game_running = True
        self._game_loop()

    def _spawn_food(self) -> tuple[int, int]:
        occupied = set(self.snake)
        if self.bonus_food:
            occupied.add(self.bonus_food)
        available = [(x, y) for x in range(GRID_WIDTH) for y in range(GRID_HEIGHT) if (x, y) not in occupied]
        return random.choice(available) if available else (0, 0)

    def _spawn_bonus_food(self):
        occupied = set(self.snake)
        occupied.add(self.food)
        available = [(x, y) for x in range(GRID_WIDTH) for y in range(GRID_HEIGHT) if (x, y) not in occupied]
        if available:
            self.bonus_food = random.choice(available)
            self.bonus_timer = 30  # ticks

    def _game_loop(self):
        if not self.game_running or self.is_paused:
            return

        self.direction = self.next_direction
        head_x, head_y = self.snake[0]

        moves = {"Up": (0, -1), "Down": (0, 1), "Left": (-1, 0), "Right": (1, 0)}
        dx, dy = moves[self.direction]
        new_head = (head_x + dx, head_y + dy)

        # Gestione bordi
        if self.wrap_var.get():
            new_head = (new_head[0] % GRID_WIDTH, new_head[1] % GRID_HEIGHT)
        else:
            if new_head[0] < 0 or new_head[0] >= GRID_WIDTH or new_head[1] < 0 or new_head[1] >= GRID_HEIGHT:
                self._game_over()
                return

        # Collisione corpo
        if new_head in self.snake:
            self._game_over()
            return

        self.snake.insert(0, new_head)

        # Mangiata mela normale
        if new_head == self.food:
            self.score += 10
            self.lbl_score.config(text=f"Punteggio: {self.score}")
            self.food = self._spawn_food()
            if not self.bonus_food and random.random() < 0.25:
                self._spawn_bonus_food()
        elif self.bonus_food and new_head == self.bonus_food:
            self.score += 50
            self.lbl_score.config(text=f"Punteggio: {self.score}")
            self.bonus_food = None
            self.bonus_timer = 0
        else:
            self.snake.pop()

        if self.bonus_food:
            self.bonus_timer -= 1
            if self.bonus_timer <= 0:
                self.bonus_food = None

        if self.score > self.high_score:
            self._save_high_score(self.score)

        self._draw_board()

        delay = SPEED_MAP.get(self.difficulty_var.get(), 80)
        self.loop_id = self.root.after(delay, self._game_loop)

    def _draw_board(self):
        self.canvas.delete("all")

        # Griglia di sfondo sottile
        for x in range(0, CANVAS_WIDTH, GRID_SIZE):
            self.canvas.create_line(x, 0, x, CANVAS_HEIGHT, fill="#1c2230", width=1)
        for y in range(0, CANVAS_HEIGHT, GRID_SIZE):
            self.canvas.create_line(0, y, CANVAS_WIDTH, y, fill="#1c2230", width=1)

        # Disegna Cibo Normale (Rossa)
        fx, fy = self.food
        pad = 3
        self.canvas.create_oval(
            fx * GRID_SIZE + pad, fy * GRID_SIZE + pad,
            (fx + 1) * GRID_SIZE - pad, (fy + 1) * GRID_SIZE - pad,
            fill="#ff4154", outline="#ff6b7d", width=2
        )

        # Disegna Cibo Bonus (Oro)
        if self.bonus_food:
            bx, by = self.bonus_food
            self.canvas.create_oval(
                bx * GRID_SIZE + 2, by * GRID_SIZE + 2,
                (bx + 1) * GRID_SIZE - 2, (by + 1) * GRID_SIZE - 2,
                fill="#ffd700", outline="#ffffff", width=2
            )

        # Disegna Serpente
        for i, (sx, sy) in enumerate(self.snake):
            x1, y1 = sx * GRID_SIZE + 1, sy * GRID_SIZE + 1
            x2, y2 = (sx + 1) * GRID_SIZE - 1, (sy + 1) * GRID_SIZE - 1
            if i == 0:
                # Testa
                self.canvas.create_rectangle(x1, y1, x2, y2, fill="#00ffaa", outline="#00d2ff", width=2)
            else:
                # Corpo
                self.canvas.create_rectangle(x1, y1, x2, y2, fill="#00b48c", outline="#0f111a", width=1)

        # Schermata iniziale se non avviato
        if not self.game_running:
            self.canvas.create_rectangle(50, CANVAS_HEIGHT // 2 - 45, CANVAS_WIDTH - 50, CANVAS_HEIGHT // 2 + 45, fill="#161b27", outline="#00ffaa", width=2)
            self.canvas.create_text(CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2 - 12, text="🐍 SNAKE GAME", font=("Segoe UI", 16, "bold"), fill="#00ffaa")
            self.canvas.create_text(CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2 + 15, text="Premi SPAZIO o 'Nuova Partita' per Iniziare!", font=("Segoe UI", 11), fill="#ffffff")

    def _game_over(self):
        self.game_running = False
        self._save_high_score(self.score)
        self.canvas.create_rectangle(40, CANVAS_HEIGHT // 2 - 50, CANVAS_WIDTH - 40, CANVAS_HEIGHT // 2 + 50, fill="#1a0d12", outline="#ff4b4b", width=2)
        self.canvas.create_text(CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2 - 15, text="💀 GAME OVER", font=("Segoe UI", 18, "bold"), fill="#ff4b4b")
        self.canvas.create_text(CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2 + 15, text=f"Punteggio Finale: {self.score} | Premi Spazio per Rigiocare", font=("Segoe UI", 11), fill="#ffffff")

if __name__ == "__main__":
    root = tk.Tk()
    app = SnakeTkinterApp(root)
    root.mainloop()
