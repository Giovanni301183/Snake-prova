"""
main.py
Interfaccia grafica principale per Snake Game realizzata con Pygame.
Grafica moderna in stile dark/neon, animazioni fluide ed effetti sonori.
"""

import sys
import os
import math
import pygame

# Assicuriamo che la cartella corrente sia nel sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, HEADER_HEIGHT, GRID_SIZE,
    GRID_WIDTH, GRID_HEIGHT, FPS, SPEED_CONFIG,
    COLOR_BG_DARK, COLOR_GRID_BG, COLOR_GRID_LINE, COLOR_HEADER_BG,
    COLOR_SNAKE_HEAD, COLOR_SNAKE_BODY_START, COLOR_SNAKE_BODY_END,
    COLOR_SNAKE_EYES, COLOR_SNAKE_EYES_WHITE, COLOR_FOOD_RED,
    COLOR_BONUS_GOLD, COLOR_LEAF, COLOR_TEXT_LIGHT, COLOR_TEXT_MUTED,
    COLOR_ACCENT, COLOR_GOLD, COLOR_RED_ALERT, COLOR_BUTTON_DEFAULT,
    COLOR_BUTTON_HOVER, COLOR_BUTTON_ACTIVE, BONUS_DURATION_SECONDS
)
from game_engine import GameEngine, UP, DOWN, LEFT, RIGHT
from sound_generator import generate_all_sounds

class SoundPlayer:
    """Carica ed esegue i suoni di gioco con gestione fallback."""
    def __init__(self, base_dir: str):
        self.sounds = {}
        self.enabled = True
        
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        except Exception as e:
            print(f"Mixer audio non disponibile: {e}")
            self.enabled = False
            return

        sound_dir = os.path.join(base_dir, "assets", "sounds")
        if not os.path.exists(sound_dir) or not os.path.exists(os.path.join(sound_dir, "eat.wav")):
            print("Generazione file audio in corso...")
            generate_all_sounds(base_dir)

        sound_names = ["eat", "bonus", "game_over", "click"]
        for name in sound_names:
            path = os.path.join(sound_dir, f"{name}.wav")
            if os.path.exists(path):
                try:
                    self.sounds[name] = pygame.mixer.Sound(path)
                except Exception as e:
                    print(f"Errore caricamento suono {name}: {e}")

    def play(self, name: str):
        if self.enabled and name in self.sounds:
            try:
                self.sounds[name].play()
            except Exception:
                pass

class Button:
    """Pulsante interattivo per i menu."""
    def __init__(self, x: int, y: int, width: int, height: int, text: str, font: pygame.font.Font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.is_hovered = False

    def check_hover(self, mouse_pos: tuple[int, int]) -> bool:
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        return self.is_hovered

    def draw(self, surface: pygame.Surface, active: bool = False):
        bg_color = COLOR_BUTTON_ACTIVE if active else (COLOR_BUTTON_HOVER if self.is_hovered else COLOR_BUTTON_DEFAULT)
        border_color = COLOR_ACCENT if (self.is_hovered or active) else (60, 75, 100)
        
        # Sfondo con angoli arrotondati
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=10)
        pygame.draw.rect(surface, border_color, self.rect, width=2, border_radius=10)
        
        # Testo centrato
        text_surf = self.font.render(self.text, True, COLOR_TEXT_LIGHT if (self.is_hovered or active) else COLOR_TEXT_MUTED)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

class SnakeGameApp:
    """Applicazione principale di Snake."""
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Snake Game - Edizione Arcade Moderna")
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        
        # Inizializzazione font di sistema ad alta leggibilità
        self.font_title = pygame.font.SysFont("Segoe UI", 46, bold=True)
        self.font_large = pygame.font.SysFont("Segoe UI", 32, bold=True)
        self.font_medium = pygame.font.SysFont("Segoe UI", 20, bold=True)
        self.font_small = pygame.font.SysFont("Segoe UI", 15)

        # Motore di gioco e audio
        scores_file = os.path.join(BASE_DIR, "scores.json")
        self.engine = GameEngine(scores_file)
        self.sound_player = SoundPlayer(BASE_DIR)
        
        # Collega i suoni alle azioni dell'engine
        self.engine.on_eat_sound = lambda: self.sound_player.play("eat")
        self.engine.on_bonus_sound = lambda: self.sound_player.play("bonus")
        self.engine.on_game_over_sound = lambda: self.sound_player.play("game_over")
        
        self.pulse_timer = 0.0
        self._init_menu_buttons()

    def _init_menu_buttons(self):
        """Inizializza i bottoni per il menu iniziale."""
        btn_w, btn_h = 240, 52
        cx = SCREEN_WIDTH // 2 - btn_w // 2
        
        self.btn_play = Button(cx, 260, btn_w, btn_h, "▶ GIOCA ORA", self.font_medium)
        
        # Bottoni Difficoltà
        diff_w = 90
        diff_start_x = SCREEN_WIDTH // 2 - (diff_w * 3 + 20) // 2
        self.btn_diffs = {
            "Facile": Button(diff_start_x, 350, diff_w, 42, "Facile", self.font_small),
            "Medio": Button(diff_start_x + diff_w + 10, 350, diff_w, 42, "Medio", self.font_small),
            "Difficile": Button(diff_start_x + (diff_w + 10) * 2, 350, diff_w, 42, "Difficile", self.font_small),
        }
        
        # Bottoni Modalità (Muri / Teletrasporto)
        mode_w = 145
        mode_start_x = SCREEN_WIDTH // 2 - (mode_w * 2 + 15) // 2
        self.btn_mode_walls = Button(mode_start_x, 435, mode_w, 42, "Muri Mortali", self.font_small)
        self.btn_mode_wrap = Button(mode_start_x + mode_w + 15, 435, mode_w, 42, "Teletrasporto", self.font_small)

        # Bottone Audio
        self.btn_audio = Button(cx, 515, btn_w, 42, "🔊 Audio: Attivo", self.font_small)

    def run(self):
        """Ciclo principale del gioco a 60 FPS."""
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0  # Delta time in secondi
            self.pulse_timer += dt * 4.0

            mouse_pos = pygame.mouse.get_pos()

            # Gestione eventi
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    self._handle_keydown(event.key)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self._handle_click(mouse_pos)

            # Aggiornamento hover bottoni
            if self.engine.state == "MENU":
                self.btn_play.check_hover(mouse_pos)
                for b in self.btn_diffs.values():
                    b.check_hover(mouse_pos)
                self.btn_mode_walls.check_hover(mouse_pos)
                self.btn_mode_wrap.check_hover(mouse_pos)
                self.btn_audio.check_hover(mouse_pos)

            # Aggiornamento logica
            self.engine.update(dt)

            # Rendering grafico
            self._render()

            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def _handle_keydown(self, key):
        """Gestione dei tasti premuti."""
        if self.engine.state == "PLAYING":
            if key in (pygame.K_UP, pygame.K_w):
                self.engine.change_direction(UP)
            elif key in (pygame.K_DOWN, pygame.K_s):
                self.engine.change_direction(DOWN)
            elif key in (pygame.K_LEFT, pygame.K_a):
                self.engine.change_direction(LEFT)
            elif key in (pygame.K_RIGHT, pygame.K_d):
                self.engine.change_direction(RIGHT)
            elif key in (pygame.K_p, pygame.K_SPACE):
                self.engine.toggle_pause()
            elif key == pygame.K_m:
                self._toggle_sound()
            elif key == pygame.K_ESCAPE:
                self.engine.state = "MENU"

        elif self.engine.state == "PAUSED":
            if key in (pygame.K_p, pygame.K_SPACE):
                self.engine.toggle_pause()
            elif key == pygame.K_ESCAPE:
                self.engine.state = "MENU"

        elif self.engine.state == "GAME_OVER":
            if key in (pygame.K_SPACE, pygame.K_RETURN):
                self.engine.reset_game()
                self.engine.state = "PLAYING"
                self.sound_player.play("click")
            elif key in (pygame.K_ESCAPE, pygame.K_m):
                self.engine.state = "MENU"
                self.sound_player.play("click")

        elif self.engine.state == "MENU":
            if key in (pygame.K_SPACE, pygame.K_RETURN):
                self.engine.reset_game()
                self.engine.state = "PLAYING"
                self.sound_player.play("click")

    def _handle_click(self, mouse_pos: tuple[int, int]):
        """Gestione dei click del mouse sui bottoni del menu."""
        if self.engine.state == "MENU":
            if self.btn_play.check_hover(mouse_pos):
                self.sound_player.play("click")
                self.engine.reset_game()
                self.engine.state = "PLAYING"

            for diff_name, btn in self.btn_diffs.items():
                if btn.check_hover(mouse_pos):
                    self.sound_player.play("click")
                    self.engine.difficulty = diff_name

            if self.btn_mode_walls.check_hover(mouse_pos):
                self.sound_player.play("click")
                self.engine.wrap_around = False
            elif self.btn_mode_wrap.check_hover(mouse_pos):
                self.sound_player.play("click")
                self.engine.wrap_around = True

            if self.btn_audio.check_hover(mouse_pos):
                self._toggle_sound()

    def _toggle_sound(self):
        """Attiva o disattiva l'audio."""
        self.engine.sound_enabled = not self.engine.sound_enabled
        self.sound_player.enabled = self.engine.sound_enabled
        status_text = "Attivo" if self.engine.sound_enabled else "Disattivato"
        icon = "🔊" if self.engine.sound_enabled else "🔇"
        self.btn_audio.text = f"{icon} Audio: {status_text}"
        if self.engine.sound_enabled:
            self.sound_player.play("click")

    # ================== RENDERING ================== #

    def _render(self):
        """Disegna la scena corrente."""
        self.screen.fill(COLOR_BG_DARK)

        if self.engine.state == "MENU":
            self._render_menu()
        else:
            self._render_gameplay()

            if self.engine.state == "PAUSED":
                self._render_pause_overlay()
            elif self.engine.state == "GAME_OVER":
                self._render_game_over_overlay()

    def _render_gameplay(self):
        """Disegna la griglia di gioco, il serpente, il cibo e l'HUD."""
        # 1. Disegna l'area di gioco e la griglia
        grid_area = pygame.Rect(0, HEADER_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT - HEADER_HEIGHT)
        pygame.draw.rect(self.screen, COLOR_GRID_BG, grid_area)

        # Linee sottili della griglia
        for x in range(0, SCREEN_WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, COLOR_GRID_LINE, (x, HEADER_HEIGHT), (x, SCREEN_HEIGHT))
        for y in range(HEADER_HEIGHT, SCREEN_HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, COLOR_GRID_LINE, (0, y), (SCREEN_WIDTH, y))

        # Bordo perimetrale (rosso se muri mortali, ciano se teletrasporto)
        border_color = (180, 50, 60) if not self.engine.wrap_around else (30, 100, 140)
        pygame.draw.rect(self.screen, border_color, grid_area, width=2)

        # 2. Disegna il Cibo Normale
        self._render_apple(self.engine.food[0], self.engine.food[1], is_bonus=False)

        # 3. Disegna il Cibo Bonus (se presente)
        if self.engine.bonus_food:
            self._render_apple(self.engine.bonus_food[0], self.engine.bonus_food[1], is_bonus=True)

        # 4. Disegna il Serpente
        self._render_snake()

        # 5. Disegna le Particelle
        for p in self.engine.particles:
            alpha_ratio = max(0.0, min(1.0, p.lifetime / p.max_lifetime))
            color = (
                int(p.color[0] * alpha_ratio),
                int(p.color[1] * alpha_ratio),
                int(p.color[2] * alpha_ratio)
            )
            pygame.draw.circle(self.screen, color, (int(p.x), int(p.y)), max(1, int(p.radius)))

        # 6. Disegna l'HUD Superiore
        self._render_hud()

    def _render_snake(self):
        """Disegna il corpo e la testa animata del serpente."""
        snake = self.engine.snake
        n = len(snake)

        for i, (gx, gy) in enumerate(reversed(snake)):
            real_index = n - 1 - i
            px = gx * GRID_SIZE
            py = gy * GRID_SIZE + HEADER_HEIGHT

            # Interpolazione colore dal capo alla coda
            ratio = real_index / max(1, n - 1)
            r = int(COLOR_SNAKE_BODY_START[0] * (1 - ratio) + COLOR_SNAKE_BODY_END[0] * ratio)
            g = int(COLOR_SNAKE_BODY_START[1] * (1 - ratio) + COLOR_SNAKE_BODY_END[1] * ratio)
            b = int(COLOR_SNAKE_BODY_START[2] * (1 - ratio) + COLOR_SNAKE_BODY_END[2] * ratio)

            rect = pygame.Rect(px + 1, py + 1, GRID_SIZE - 2, GRID_SIZE - 2)

            if real_index == 0:
                # Testa
                pygame.draw.rect(self.screen, COLOR_SNAKE_HEAD, rect, border_radius=7)
                self._render_snake_eyes(px, py)
            else:
                # Corpo
                pygame.draw.rect(self.screen, (r, g, b), rect, border_radius=5)

    def _render_snake_eyes(self, px: int, py: int):
        """Disegna gli occhi della testa che guardano nella direzione di movimento."""
        dx, dy = self.engine.direction
        eye_radius = 3
        pupil_radius = 1.5

        if dx == 1:  # Destra
            left_eye = (px + 18, py + 7)
            right_eye = (px + 18, py + 17)
            pupil_offset = (1, 0)
        elif dx == -1:  # Sinistra
            left_eye = (px + 7, py + 7)
            right_eye = (px + 7, py + 17)
            pupil_offset = (-1, 0)
        elif dy == -1:  # Su
            left_eye = (px + 7, py + 7)
            right_eye = (px + 17, py + 7)
            pupil_offset = (0, -1)
        else:  # Giù
            left_eye = (px + 7, py + 18)
            right_eye = (px + 17, py + 18)
            pupil_offset = (0, 1)

        for eye in (left_eye, right_eye):
            pygame.draw.circle(self.screen, COLOR_SNAKE_EYES_WHITE, eye, eye_radius)
            pupil = (eye[0] + pupil_offset[0], eye[1] + pupil_offset[1])
            pygame.draw.circle(self.screen, COLOR_SNAKE_EYES, pupil, pupil_radius)

    def _render_apple(self, gx: int, gy: int, is_bonus: bool = False):
        """Disegna una mela o mela dorata bonus con animazione pulsante."""
        px = gx * GRID_SIZE
        py = gy * GRID_SIZE + HEADER_HEIGHT

        center_x = px + GRID_SIZE // 2
        center_y = py + GRID_SIZE // 2 + 1

        # Effetto pulsazione morbida
        pulse = math.sin(self.pulse_timer) * (1.5 if is_bonus else 0.8)
        radius = (GRID_SIZE // 2 - 2) + pulse

        color = COLOR_BONUS_GOLD if is_bonus else COLOR_FOOD_RED

        # Corpo della mela
        pygame.draw.circle(self.screen, color, (int(center_x), int(center_y)), max(3, int(radius)))

        # Foglia verde
        leaf_rect = pygame.Rect(center_x + 1, center_y - radius - 1, 4, 3)
        pygame.draw.ellipse(self.screen, COLOR_LEAF, leaf_rect)

        # Bagliore aggiuntivo per mela bonus
        if is_bonus:
            pygame.draw.circle(self.screen, (255, 255, 200), (int(center_x - 2), int(center_y - 2)), 2)

    def _render_hud(self):
        """Disegna la barra superiore delle statistiche."""
        header_rect = pygame.Rect(0, 0, SCREEN_WIDTH, HEADER_HEIGHT)
        pygame.draw.rect(self.screen, COLOR_HEADER_BG, header_rect)
        pygame.draw.line(self.screen, (40, 50, 70), (0, HEADER_HEIGHT - 1), (SCREEN_WIDTH, HEADER_HEIGHT - 1), 2)

        # Punteggio corrente
        score_title = self.font_small.render("PUNTEGGIO", True, COLOR_TEXT_MUTED)
        score_val = self.font_large.render(str(self.engine.score), True, COLOR_TEXT_LIGHT)
        self.screen.blit(score_title, (25, 10))
        self.screen.blit(score_val, (25, 28))

        # Record / High Score
        record_title = self.font_small.render("RECORD", True, COLOR_GOLD)
        record_val = self.font_large.render(str(self.engine.high_score), True, COLOR_GOLD)
        self.screen.blit(record_title, (180, 10))
        self.screen.blit(record_val, (180, 28))

        # Modalità e Difficoltà
        mode_text = f"Modo: {'Teletrasporto' if self.engine.wrap_around else 'Muri Mortali'} | Difficoltà: {self.engine.difficulty}"
        mode_surf = self.font_small.render(mode_text, True, COLOR_TEXT_MUTED)
        self.screen.blit(mode_surf, (340, 14))

        # Indicatore Mute / Comandi
        help_text = "P: Pausa | M: Audio | ESC: Menu"
        help_surf = self.font_small.render(help_text, True, COLOR_ACCENT)
        self.screen.blit(help_surf, (340, 36))

        # Barra di timer per bonus mela
        if self.engine.bonus_food:
            bar_w = 120
            bar_h = 10
            bar_x = SCREEN_WIDTH - bar_w - 25
            bar_y = 35
            
            ratio = max(0.0, min(1.0, self.engine.bonus_timer / BONUS_DURATION_SECONDS))
            bonus_lbl = self.font_small.render(f"BONUS STAR! {int(self.engine.bonus_timer)}s", True, COLOR_BONUS_GOLD)
            self.screen.blit(bonus_lbl, (bar_x, 12))

            pygame.draw.rect(self.screen, (40, 45, 60), (bar_x, bar_y, bar_w, bar_h), border_radius=4)
            pygame.draw.rect(self.screen, COLOR_BONUS_GOLD, (bar_x, bar_y, int(bar_w * ratio), bar_h), border_radius=4)

    def _render_menu(self):
        """Disegna il Menu Iniziale moderno."""
        # Titolo Gioco con effetto Neon
        title_surf = self.font_title.render("🐍 SNAKE ARCADE", True, COLOR_SNAKE_HEAD)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 90))
        self.screen.blit(title_surf, title_rect)

        sub_surf = self.font_small.render("Edizione Moderna in Python - Creato con cura", True, COLOR_TEXT_MUTED)
        sub_rect = sub_surf.get_rect(center=(SCREEN_WIDTH // 2, 140))
        self.screen.blit(sub_surf, sub_rect)

        # Record Attuale
        high_surf = self.font_medium.render(f"🏆 Record Attuale: {self.engine.high_score}", True, COLOR_GOLD)
        high_rect = high_surf.get_rect(center=(SCREEN_WIDTH // 2, 190))
        self.screen.blit(high_surf, high_rect)

        # Bottone Gioca
        self.btn_play.draw(self.screen)

        # Selettore Difficoltà
        diff_label = self.font_small.render("SELEZIONA DIFFICOLTÀ:", True, COLOR_TEXT_MUTED)
        self.screen.blit(diff_label, (SCREEN_WIDTH // 2 - 130, 325))
        for name, btn in self.btn_diffs.items():
            btn.draw(self.screen, active=(self.engine.difficulty == name))

        # Selettore Modalità Muri
        mode_label = self.font_small.render("MODALITÀ BORDI:", True, COLOR_TEXT_MUTED)
        self.screen.blit(mode_label, (SCREEN_WIDTH // 2 - 130, 410))
        self.btn_mode_walls.draw(self.screen, active=(not self.engine.wrap_around))
        self.btn_mode_wrap.draw(self.screen, active=self.engine.wrap_around)

        # Bottone Audio
        self.btn_audio.draw(self.screen)

        # Istruzioni comandi in basso
        footer_surf = self.font_small.render("Controlli: Frecce Direzionali o W A S D | P: Pausa", True, (100, 115, 140))
        footer_rect = footer_surf.get_rect(center=(SCREEN_WIDTH // 2, 630))
        self.screen.blit(footer_surf, footer_rect)

    def _render_pause_overlay(self):
        """Overlay scuro per lo stato di Pausa."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 12, 18, 180))
        self.screen.blit(overlay, (0, 0))

        box = pygame.Rect(SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT // 2 - 80, 360, 160)
        pygame.draw.rect(self.screen, (24, 30, 44), box, border_radius=12)
        pygame.draw.rect(self.screen, COLOR_ACCENT, box, width=2, border_radius=12)

        pause_title = self.font_large.render("⏸ GIOCO IN PAUSA", True, COLOR_TEXT_LIGHT)
        pause_rect = pause_title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 25))
        self.screen.blit(pause_title, pause_rect)

        sub_text = self.font_small.render("Premi SPAZIO o P per riprendere", True, COLOR_TEXT_MUTED)
        sub_rect = sub_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 25))
        self.screen.blit(sub_text, sub_rect)

    def _render_game_over_overlay(self):
        """Overlay scuro con badge punteggio per il Game Over."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((15, 8, 10, 200))
        self.screen.blit(overlay, (0, 0))

        box = pygame.Rect(SCREEN_WIDTH // 2 - 220, SCREEN_HEIGHT // 2 - 140, 440, 280)
        pygame.draw.rect(self.screen, (28, 22, 26), box, border_radius=15)
        pygame.draw.rect(self.screen, COLOR_RED_ALERT, box, width=2, border_radius=15)

        go_surf = self.font_large.render("💀 GAME OVER", True, COLOR_RED_ALERT)
        go_rect = go_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 90))
        self.screen.blit(go_surf, go_rect)

        score_surf = self.font_medium.render(f"Punteggio Finale: {self.engine.score}", True, COLOR_TEXT_LIGHT)
        score_rect = score_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
        self.screen.blit(score_surf, score_rect)

        if self.engine.is_new_high_score:
            rec_surf = self.font_medium.render("🎉 NUOVO RECORD RAGGIUNTO! 🎉", True, COLOR_GOLD)
            rec_rect = rec_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(rec_surf, rec_rect)
        else:
            rec_surf = self.font_small.render(f"Miglior Record: {self.engine.high_score}", True, COLOR_TEXT_MUTED)
            rec_rect = rec_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(rec_surf, rec_rect)

        hint1 = self.font_medium.render("Premi SPAZIO o INVIO per Rigiocare", True, COLOR_SNAKE_HEAD)
        hint1_rect = hint1.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 55))
        self.screen.blit(hint1, hint1_rect)

        hint2 = self.font_small.render("Premi ESC per tornare al Menu Principale", True, COLOR_TEXT_MUTED)
        hint2_rect = hint2.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 95))
        self.screen.blit(hint2, hint2_rect)

if __name__ == "__main__":
    app = SnakeGameApp()
    app.run()
