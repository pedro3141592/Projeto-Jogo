import pygame
from PPlay.window import Window
from PPlay.keyboard import Keyboard
from PPlay.mouse import Mouse
from src.config import WIDTH, HEIGHT


class Game:
    def __init__(self):
        self.window   = Window(WIDTH, HEIGHT, "Noite Eterna")
        self.keyboard = Keyboard()
        self.mouse    = Mouse()
        pygame.font.init()
        self.fonts = {
            "normal": pygame.font.SysFont("Arial", 22),
            "grande": pygame.font.SysFont("Arial", 42, bold=True),
        }
        self._state = None
        self._next_state = None
        self.running = True

    def change_state(self, new_state):
        self._next_state = new_state

    def _apply_pending(self):
        if self._next_state is None:
            return
        if self._state is not None:
            self._state.exit()
        self._state = self._next_state
        self._state.game = self
        self._state.enter()
        self._next_state = None

    def run(self, initial_state):
        self._state = initial_state
        self._state.game = self
        self._state.enter()
        while self.running:
            dt = self.window.delta_time()
            self._state.handle_input()
            self._state.update(dt)
            self.window.set_background_color((0, 0, 0))
            self._state.draw()
            self.window.update()
            self._apply_pending()