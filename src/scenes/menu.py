import pygame
from src.core.state import State
from src.config import (
    WIDTH, HEIGHT, COR_FUNDO, COR_TEXTO, COR_DESTAQUE,
)
from src.scenes.gameplay import GameplayScene


class MenuScene(State):
    def enter(self, **kwargs):
        self.speedrun = False
        # botões como rects (pygame.draw.rect)
        self.btns = [
            {"rect": pygame.Rect(WIDTH // 2 - 170, 300, 340, 70),
             "texto": "JOGAR",       "acao": "jogar"},
            {"rect": pygame.Rect(WIDTH // 2 - 170, 400, 340, 70),
             "texto": "SPEEDRUN",    "acao": "speedrun"},
            {"rect": pygame.Rect(WIDTH // 2 - 170, 500, 340, 70),
             "texto": "SAIR",        "acao": "sair"},
        ]
        self._clique_anterior = False

    def _clicou_agora(self):
        p = self.game.mouse.button_pressed(1)
        r = p and not self._clique_anterior
        self._clique_anterior = p
        return r

    def _mouse_no_rect(self, rect):
        mx, my = pygame.mouse.get_pos()
        return rect.collidepoint(mx, my)

    def handle_input(self):
        if not self._clicou_agora():
            return
        for b in self.btns:
            if not self._mouse_no_rect(b["rect"]):
                continue
            if b["acao"] == "jogar":
                self.game.change_state(GameplayScene(
                    self.game, level_id=1, speedrun=self.speedrun))
            elif b["acao"] == "speedrun":
                self.speedrun = not self.speedrun
            elif b["acao"] == "sair":
                self.game.running = False

    def update(self, dt):
        pass

    def draw(self):
        g = self.game
        w = g.window
        w.set_background_color(COR_FUNDO)

        # título
        t1 = g.fonts["grande"].render(
            "NOITE ETERNA", True, COR_DESTAQUE)
        w.screen.blit(t1, (WIDTH // 2 - t1.get_width() // 2, 80))
        t2 = g.fonts["normal"].render(
            "A ameaça cítrica", True, COR_TEXTO)
        w.screen.blit(t2, (WIDTH // 2 - t2.get_width() // 2, 140))

        # botões
        for b in self.btns:
            hover = self._mouse_no_rect(b["rect"])
            cor = (140, 40, 40) if hover else (90, 30, 30)
            pygame.draw.rect(w.screen, cor, b["rect"])
            pygame.draw.rect(w.screen, (220, 200, 200), b["rect"], 2)

            label = b["texto"]
            if b["acao"] == "speedrun":
                label += f": {'ON' if self.speedrun else 'OFF'}"
            txt = g.fonts["normal"].render(label, True, COR_TEXTO)
            w.screen.blit(txt, (
                b["rect"].x + b["rect"].width // 2 - txt.get_width() // 2,
                b["rect"].y + b["rect"].height // 2 - txt.get_height() // 2,
            ))

        # controles
        ajuda = [
            "SETAS: mover / pular (arco fixo) / agachar",
            "ESPAÇO: chicote (com delay — acerte a ponta para parry!)",
            "X ou Z: machadinha (consome corações)",
            "ESC: voltar ao menu",
        ]
        y = HEIGHT - 160
        for linha in ajuda:
            s = g.fonts["normal"].render(linha, True, (180, 180, 180))
            w.screen.blit(s, (40, y))
            y += 32