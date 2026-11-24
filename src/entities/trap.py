import pygame


class Armadilha:
    def __init__(self, x, y, width=48, height=18):
        self.rect = pygame.Rect(int(x), int(y), int(width), int(height))

    def draw(self, window):
        r = self.rect
        # Base metálica escura
        pygame.draw.rect(window.screen, (90, 95, 110), (r.x, r.bottom - 6, r.width, 6))

        # Pontas de espinho (estilo 8-bits de alto contraste)
        largura_dente = 12
        num_dentes = max(1, r.width // largura_dente)
        for i in range(num_dentes):
            x0 = r.x + i * largura_dente
            x1 = min(r.right, x0 + largura_dente)
            xm = (x0 + x1) // 2
            pontos = [(x0, r.bottom - 6), (xm, r.top), (x1, r.bottom - 6)]
            pygame.draw.polygon(window.screen, (215, 220, 235), pontos)
            pygame.draw.polygon(window.screen, (45, 20, 25), pontos, 1)