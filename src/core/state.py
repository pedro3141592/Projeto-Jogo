class State:
    def __init__(self, game):
        self.game = game

    def enter(self, **kwargs): pass
    def exit(self): pass
    def handle_input(self): pass
    def update(self, dt): pass
    def draw(self): pass