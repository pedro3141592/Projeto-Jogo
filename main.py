from src.assets import garantir_assets
from src.core.game import Game
from src.scenes.menu import MenuScene

if __name__ == "__main__":
    garantir_assets()
    Game().run(MenuScene(None))