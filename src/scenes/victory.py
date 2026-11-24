from src.core.state import State
from src.config import WIDTH, HEIGHT, COR_TEXTO, COR_DESTAQUE
from src.scenes.menu import MenuScene


class VictoryScene(State):
    def __init__(self, game, tempo_speedrun=0.0, speedrun=False):
        super().__init__(game)
        self.tempo_speedrun = tempo_speedrun
        self.speedrun = speedrun

    def enter(self, **kwargs):
        pass

    def handle_input(self):
        if self.game.keyboard.key_pressed("ESC") or \
           self.game.keyboard.key_pressed("ENTER"):
            self.game.change_state(MenuScene(self.game))

    def update(self, dt):
        pass

    def draw(self):
        g = self.game
        w = g.window
        w.set_background_color((10, 20, 10))

        t = g.fonts["grande"].render(
            "VITÓRIA!", True, COR_DESTAQUE)
        w.screen.blit(t, (WIDTH // 2 - t.get_width() // 2, 200))

        sub = g.fonts["normal"].render(
            "O Cálice de Sangue foi destruído. As laranjas do condado "
            "estão a salvo.", True, COR_TEXTO)
        w.screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 320))

        if self.speedrun:
            st = g.fonts["grande"].render(
                f"{self.tempo_speedrun:06.2f}s", True, COR_DESTAQUE)
            w.screen.blit(st, (WIDTH // 2 - st.get_width() // 2, 420))

        dica = g.fonts["normal"].render(
            "ENTER para voltar ao menu", True, (180, 180, 180))
        w.screen.blit(dica, (WIDTH // 2 - dica.get_width() // 2, 600))