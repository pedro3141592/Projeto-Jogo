import pygame
from src.core.state import State
from src.config import WIDTH, HEIGHT, COR_TEXTO, COR_DESTAQUE
from src.scenes.menu import MenuScene
from src.scenes.gameplay import GameplayScene


class GameOverScene(State):
    def __init__(self, game, tempo_speedrun=0.0, speedrun=False):
        super().__init__(game)
        self.tempo_speedrun = tempo_speedrun
        self.speedrun = speedrun
        self.escolha = 0  # 0=tentar de novo, 1=menu
        self._clique_anterior = False

    def enter(self, **kwargs):
        self._clique_anterior = False

    def _clicou_agora(self):
        p = self.game.mouse.button_pressed(1)
        r = p and not self._clique_anterior
        self._clique_anterior = p
        return r

    def handle_input(self):
        kb = self.game.keyboard
        if kb.key_pressed("LEFT"):
            self.escolha = 0
        if kb.key_pressed("RIGHT"):
            self.escolha = 1
        if kb.key_pressed("ENTER") or kb.key_pressed("SPACE"):
            self._aplicar()
        if kb.key_pressed("ESC"):
            self.game.change_state(MenuScene(self.game))

    def _aplicar(self):
        if self.escolha == 0:
            self.game.change_state(GameplayScene(
                self.game, level_id=1, speedrun=self.speedrun))
        else:
            self.game.change_state(MenuScene(self.game))

    def update(self, dt):
        pass

    def draw(self):
        g = self.game
        w = g.window
        w.set_background_color((30, 0, 0))

        t = g.fonts["grande"].render("GAME OVER", True, COR_DESTAQUE)
        w.screen.blit(t, (WIDTH // 2 - t.get_width() // 2, 180))

        sub = g.fonts["normal"].render(
            "Naim caiu...", True, COR_TEXTO)
        w.screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 260))

        if self.speedrun:
            st = g.fonts["normal"].render(
                f"Tempo: {self.tempo_speedrun:06.2f}s",
                True, (200, 200, 200))
            w.screen.blit(st, (WIDTH // 2 - st.get_width() // 2, 320))

        for i, texto in enumerate(["TENTAR DE NOVO", "MENU"]):
            sel = (i == self.escolha)
            cor = COR_DESTAQUE if sel else COR_TEXTO
            s = g.fonts["normal"].render(texto, True, cor)
            x = WIDTH // 2 - 220 + i * 240
            w.screen.blit(s, (x, 460))
            if sel:
                pygame.draw.rect(w.screen, COR_DESTAQUE,
                                 (x - 10, 452, s.get_width() + 20, 40), 2)

        dica = g.fonts["normal"].render(
            "<- -> navegar  |  ENTER confirmar",
            True, (150, 150, 150))
        w.screen.blit(dica, (WIDTH // 2 - dica.get_width() // 2, 600))