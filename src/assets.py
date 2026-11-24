import os
import struct
import zlib
import pygame

FALLBACKS = {
    "assets/images/player/player.png":            ((32, 48),  (40, 120, 200)),
    "assets/images/enemies/bat.png":              ((32, 24),  (140, 60, 160)),
    "assets/images/enemies/zombie.png":           ((32, 48),  (80, 140, 60)),
    "assets/images/enemies/skeleton.png":         ((32, 48),  (210, 210, 210)),
    "assets/images/enemies/boss.png":             ((80, 128), (180, 40, 40)),
    "assets/images/projectiles/bone.png":         ((14, 14),  (240, 240, 210)),
    "assets/images/projectiles/axe.png":          ((18, 18),  (190, 180, 100)),
    "assets/images/projectiles/boss_shot.png":    ((16, 16),  (220, 60, 60)),
    "assets/images/ui/botao1.png":                ((320, 70), (90, 30, 30)),
    "assets/images/ui/botao2.png":                ((320, 70), (30, 90, 30)),
    "assets/images/ui/botao3.png":                ((320, 70), (60, 60, 110)),
}

def _criar_png_nativo(path, size, color):
    """Cria um PNG válido usando apenas a biblioteca padrão do Python."""
    width, height = size
    r, g, b = color
    
    # Prepara os dados brutos da imagem (RGBA)
    raw_data = b''
    for y in range(height):
        raw_data += b'\x00'  # Filtro (None)
        for x in range(width):
            raw_data += bytes([r, g, b, 255])
            
    def chunk(chunk_type, data):
        c = chunk_type + data
        crc = struct.pack('>I', zlib.crc32(c) & 0xffffffff)
        return struct.pack('>I', len(data)) + c + crc

    header = b'\x89PNG\r\n\x1a\n'
    # color type 6 = RGBA
    ihdr = chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0))
    idat = chunk(b'IDAT', zlib.compress(raw_data))
    iend = chunk(b'IEND', b'')

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as f:
        f.write(header + ihdr + idat + iend)

def garantir_assets():
    pygame.init()
    for path, (size, color) in FALLBACKS.items():
        # Se o arquivo já existe (como os seus do player), ele não faz nada
        if not os.path.exists(path):
            _criar_png_nativo(path, size, color)