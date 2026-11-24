# ---------- Tela ----------
WIDTH, HEIGHT = 1280, 720
HUD_HEIGHT = 60

# ---------- Física ----------
GRAVITY      = 1400
PLAYER_SPEED = 140
JUMP_FORCE   = 650
FLOOR_Y      = 640

# ---------- Player ----------
PLAYER_HP            = 8
INVULN_TIME          = 1.5
AXES_INICIAIS        = 5
CROUCH_HEIGHT_FACTOR = 0.5

# ---------- Chicote ----------
WHIP_WINDUP       = 0.20       # Tempo puxando o braço / atraso inicial
WHIP_ACTIVE       = 0.20       # Tempo da fase ativa do chicote
WHIP_COOLDOWN     = 0.20       # Tempo recolhendo
WHIP_RANGE        = 90        # Alcance do chicote
WHIP_TIP_FRACTION = 0.4        # 40% finais = ponta (parry)

# ---------- Boss ----------
BOSS_GUARDA_ABERTA_TEMPO = 30.0
BOSS_DANO_WHIP           = 1
BOSS_DANO_REFLETIDO      = 2

# ---------- Cores ----------
COR_FUNDO       = (10, 5, 20)
COR_HUD         = (0, 0, 0)
COR_TEXTO       = (255, 255, 255)
COR_DESTAQUE    = (255, 215, 0)
COR_VIDA        = (200, 30, 30)
COR_VIDA_VAZIA  = (60, 20, 20)
COR_CHICOTE     = (230, 210, 140)
COR_PLATAFORMA  = (80, 50, 40)
COR_SANGRENTO   = (180, 40, 40)

# ---------- Definição das 3 telas ----------
LEVELS = [
    {
        "nome": "Pátio do Castelo",
        "plataformas": [(0, FLOOR_Y, WIDTH, HEIGHT - FLOOR_Y)],
        "armadilhas": [],
        "inimigos": [
            ("bat",    300, 200),
            ("bat",    700, 150),
            ("bat",   1000, 250),
            ("zombie", 600, FLOOR_Y - 48),
            ("zombie", 900, FLOOR_Y - 48),
        ],
    },
    {
        "nome": "Corredor das Armaduras",
        "plataformas": [
            (0,    FLOOR_Y,        WIDTH, HEIGHT - FLOOR_Y),
            (180,  FLOOR_Y - 140,  240,   24),
            (560,  FLOOR_Y - 240,  240,   24),
            (940,  FLOOR_Y - 140,  240,   24),
        ],
        "armadilhas": [
            # Armadilhas no chão entre as plataformas
            (450, FLOOR_Y - 18, 60, 18),
            (730, FLOOR_Y - 18, 60, 18),
            # Armadilha em uma das plataformas elevadas para exigir salto/desvio
            (650, FLOOR_Y - 240 - 18, 48, 18),
        ],
        "inimigos": [
            ("skeleton", 300,  FLOOR_Y - 48),
            ("skeleton", 800,  FLOOR_Y - 48),
            ("skeleton", 1040, FLOOR_Y - 140 - 48),
        ],
    },
    {
        "nome": "Sala do Trono",
        "plataformas": [(0, FLOOR_Y, WIDTH, HEIGHT - FLOOR_Y)],
        "armadilhas": [],
        "inimigos": [
            ("boss", WIDTH - 250, FLOOR_Y - 128),
        ],
    },
]