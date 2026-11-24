import pygame
from PPlay.sprite import Sprite
from src.config import WIDTH, HEIGHT


_PATH = {
    "bone":      "assets/images/projectiles/bone.png",
    "axe":       "assets/images/projectiles/axe.png",
    "boss_shot": "assets/images/projectiles/boss_shot.png",
}


class Projectile(Sprite):
    def __init__(self, tipo, x, y, direcao):
        super().__init__(_PATH[tipo], 1)
        self.tipo      = tipo
        self.escala    = 2 if tipo == "axe" else 1
        self._frame_w  = self.width
        self._frame_h  = self.height
        self.width     = self._frame_w * self.escala
        self.height    = self._frame_h * self.escala

        self.x         = x - self.width // 2
        self.y         = y
        self.direcao   = direcao
        self.vivo      = True
        self.refletido = False

        if tipo == "axe":
            self.vx, self.vy, self.gravidade = 380 * direcao, -550, 1400
        elif tipo == "bone":
            self.vx, self.vy, self.gravidade = 260 * direcao, -220, 1200
        elif tipo == "boss_shot":
            self.vx, self.vy, self.gravidade = 340 * direcao, 0, 0

    def refletir(self):
        self.refletido = True
        self.vx = -self.vx * 1.8
        self.vy = 0
        self.gravidade = 0
        self.direcao = -self.direcao

    def update(self, dt):
        self.vy += self.gravidade * dt
        self.x  += self.vx * dt
        self.y  += self.vy * dt
        if (self.x < -100 or self.x > WIDTH + 100
                or self.y < -100 or self.y > HEIGHT + 100):
            self.vivo = False

    def hitbox(self):
        return pygame.Rect(int(self.x), int(self.y),
                           self.width, self.height)

    def draw(self, screen=None):
        if self.escala == 1:
            super().draw()
            return

        destino = screen if screen is not None else pygame.display.get_surface()
        if destino is None:
            return

        surf_scaled = pygame.transform.scale(
            self.image, (self.width, self.height)
        )
        if self.direcao == -1:
            surf_scaled = pygame.transform.flip(surf_scaled, True, False)

        destino.blit(surf_scaled, (int(self.x), int(self.y)))