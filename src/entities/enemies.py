import math
import random
import pygame
from PPlay.sprite import Sprite
from src.config import (
    WIDTH, FLOOR_Y,
    BOSS_GUARDA_ABERTA_TEMPO,
)
from src.entities.projectile import Projectile


class Inimigo(Sprite):
    TIPO   = "base"
    HP_INI = 1
    PONTOS = 10

    def __init__(self, tipo_arquivo, x, y, frames=1, escala=1):
        super().__init__(f"assets/images/enemies/{tipo_arquivo}.png", frames)
        self._num_frames = max(1, frames)
        if self._num_frames > 1:
            self.set_total_duration(400)

        self.escala = escala
        self._frame_w = self.width
        self._frame_h = self.height
        self.width = self._frame_w * self.escala
        self.height = self._frame_h * self.escala

        self.x = x
        self.y = y
        self.hp = self.HP_INI
        self.vivo = True
        self.facing = 1
        self.stun_ate = 0.0
        self.play()

    def esta_atordoado(self, tempo):
        return tempo < self.stun_ate

    def update(self, dt, player, projeteis, tempo):
        super().update()

    def levar_dano(self, dano=1, tempo=None, duracao_stun=0.25):
        self.hp -= dano
        if tempo is not None and duracao_stun > 0:
            self.stun_ate = max(self.stun_ate, tempo + duracao_stun)
        if self.hp <= 0:
            self.vivo = False

    def hitbox(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def draw(self, window):
        frame_idx = max(0, min(self.get_curr_frame(), self._num_frames - 1))
        frame_x = frame_idx * self._frame_w
        surf_frame = self.image.subsurface(
            pygame.Rect(frame_x, 0, self._frame_w, self._frame_h)
        )
        draw_w = self._frame_w * self.escala
        draw_h = self._frame_h * self.escala
        if self.escala != 1:
            surf_frame = pygame.transform.scale(surf_frame, (draw_w, draw_h))

        if self.facing == -1:
            surf_frame = pygame.transform.flip(surf_frame, True, False)

        draw_x = int(self.x)
        draw_y = int(self.y + self.height - draw_h)
        window.screen.blit(surf_frame, (draw_x, draw_y))


# ---------------- TELA 1 ----------------
class Morcego(Inimigo):
    TIPO, HP_INI, PONTOS = "bat", 1, 20

    def __init__(self, x, y):
        super().__init__("bat", x, y, frames=2, escala=1)
        self.x_base = x
        self.y_base = y
        self.t = random.uniform(0, math.tau)
        self.vel_x = 110

    def update(self, dt, player, projeteis, tempo):
        super().update(dt, player, projeteis, tempo)
        self.t += dt
        self.x_base -= self.vel_x * dt
        if self.x_base < -50:
            self.x_base = WIDTH + 50
        self.x = self.x_base
        self.y = self.y_base + 40 * math.sin(self.t * 2.5)

        self.facing = -1 if self.vel_x > 0 else 1


class Zumbi(Inimigo):
    TIPO, HP_INI, PONTOS = "zombie", 2, 30

    def __init__(self, x, y):
        super().__init__("zombie", x, y, frames=2, escala=2)
        self.y = FLOOR_Y - self.height

    def update(self, dt, player, projeteis, tempo):
        super().update(dt, player, projeteis, tempo)
        self.y = FLOOR_Y - self.height
        if self.esta_atordoado(tempo):
            return
        dx = player.x - self.x
        if abs(dx) > 20:
            self.x += 45 * dt * (1 if dx > 0 else -1)
            self.facing = 1 if dx > 0 else -1


# ---------------- TELA 2 ----------------
class Esqueleto(Inimigo):
    TIPO, HP_INI, PONTOS = "skeleton", 2, 40

    def __init__(self, x, y):
        super().__init__("skeleton", x, y, frames=2, escala=2)
        superficie_y = y + 48
        self.y = superficie_y - self.height
        self.tempo_ataque = random.uniform(1.0, 2.0)

    def update(self, dt, player, projeteis, tempo):
        super().update(dt, player, projeteis, tempo)
        self.facing = 1 if player.x > self.x else -1

        if self.esta_atordoado(tempo):
            return

        self.tempo_ataque -= dt
        if self.tempo_ataque <= 0:
            projeteis.append(Projectile(
                "bone", self.x + self.width // 2,
                self.y + self.height // 3, self.facing))
            self.tempo_ataque = random.uniform(1.8, 2.8)


# ---------------- TELA 3 ----------------
class LordeNayatuhen(Inimigo):
    TIPO, HP_INI, PONTOS = "boss", 20, 500

    def __init__(self, x, y):
        super().__init__("boss", x, y, frames=2, escala=2)
        self.stop()
        self.set_curr_frame(1)
        self.y = FLOOR_Y - self.height
        self.x_ancora = min(x, WIDTH - self.width - 80)
        self.tempo_ataque = 1.4
        self.tempo_pose_ataque = 0.0
        self.guarda_aberta_ate = 0.0

    def update(self, dt, player, projeteis, tempo):
        # Não chama super().update() para evitar avanço automático de frame
        self.facing = 1 if player.x > self.x else -1

        # Leve deslocamento tático na Sala do Trono
        if not self.guarda_aberta(tempo):
            alvo_x = self.x_ancora + 60 * math.sin(tempo * 1.4)
            self.x = max(220, min(WIDTH - self.width - 40, alvo_x))
        self.y = FLOOR_Y - self.height

        if self.tempo_pose_ataque > 0:
            self.tempo_pose_ataque = max(0.0, self.tempo_pose_ataque - dt)
            self.set_curr_frame(0 if self.tempo_pose_ataque > 0 else 1)
        else:
            self.set_curr_frame(1)

        self.tempo_ataque -= dt
        if self.tempo_ataque <= 0:
            origem_x = self.x if self.facing == -1 else self.x + self.width
            origem_y_alta = int(self.y + self.height * 0.45)
            # Bola de fogo baixa próxima ao chão para exigir salto (mesmo agachado atinge)
            origem_y_baixa = FLOOR_Y - 22

            projeteis.append(Projectile(
                "boss_shot", origem_x, origem_y_alta, self.facing))
            self.tempo_pose_ataque = 0.35
            self.tempo_ataque = random.uniform(1.8, 2.5)

    def abrir_guarda(self, tempo):
        self.guarda_aberta_ate = tempo + BOSS_GUARDA_ABERTA_TEMPO

    def guarda_aberta(self, tempo):
        return tempo < self.guarda_aberta_ate

    def draw(self, window):
        super().draw(window)
        # Destaque visual quando a guarda está aberta após parry/reflexão
        if self.guarda_aberta(pygame.time.get_ticks() / 1000.0):
            rect_destaque = pygame.Rect(
                int(self.x) - 4, int(self.y) - 4,
                self.width + 8, self.height + 8
            )
            pygame.draw.rect(window.screen, (255, 215, 0), rect_destaque, 2)