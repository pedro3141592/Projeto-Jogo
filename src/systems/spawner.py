from PPlay.sprite import Sprite
from src.config import WIDTH, TOPO_INICIAL

def criar_matriz_monstros(cfg, path):
    base = Sprite(path, 1)
    w, h = base.width, base.height
    gap_x, gap_y = w // 2, h // 2
    L, C = cfg["linhas"], cfg["colunas"]
    largura_total = C * w + (C - 1) * gap_x
    offset_x = (WIDTH - largura_total) // 2
    offset_y = TOPO_INICIAL
    matriz = []
    for i in range(L):
        linha = []
        for j in range(C):
            m = Sprite(path, 1)
            m.set_position(offset_x + j * (w + gap_x),
                           offset_y + i * (h + gap_y))
            linha.append(m)
        matriz.append(linha)
    return matriz

def monstros_vivos(matriz):
    for linha in matriz:
        for m in linha:
            if m is not None:
                yield m