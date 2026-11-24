import math
import os
import struct
import wave
import pygame
from src.core.state import State
from src.config import (
    WIDTH, HEIGHT, HUD_HEIGHT, FLOOR_Y,
    LEVELS, COR_FUNDO, COR_HUD, COR_TEXTO, COR_DESTAQUE,
    COR_VIDA, COR_VIDA_VAZIA, COR_PLATAFORMA, COR_SANGRENTO,
    BOSS_DANO_WHIP, BOSS_DANO_REFLETIDO,
)
from src.entities.player import Player
from src.entities.enemies import (
    Morcego, Zumbi, Esqueleto, LordeNayatuhen,
)
from src.entities.projectile import Projectile
from src.entities.trap import Armadilha


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
AUDIO_DIR = os.path.join(BASE_DIR, "assets", "audio")


def _gerar_wav_loop_8bit(caminho, frequencias, duracao_nota=0.18, volume=0.2):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    sample_rate = 22050
    samples_por_nota = int(sample_rate * duracao_nota)

    with wave.open(caminho, "w") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)

        frames = bytearray()
        for freq in frequencias:
            for i in range(samples_por_nota):
                if freq <= 0:
                    amostra = 0.0
                else:
                    t = i / sample_rate
                    # Onda quadrada 8-bit simples
                    onda = 1.0 if math.sin(2.0 * math.pi * freq * t) >= 0 else -1.0
                    env = min(1.0, i / (sample_rate * 0.01))
                    amostra = onda * env * volume
                valor = int(max(-32767, min(32767, amostra * 32767)))
                frames.extend(struct.pack("<h", valor))

        wav_file.writeframes(frames)


def _resolver_arquivo_musica(base_nome):
    candidatos = [
        os.path.join(AUDIO_DIR, f"{base_nome}.ogg"),
        os.path.join(AUDIO_DIR, f"{base_nome}.mp3"),
        os.path.join(AUDIO_DIR, f"{base_nome}.wav"),
        os.path.join(BASE_DIR, "assets", "sounds", f"{base_nome}.ogg"),
        os.path.join(BASE_DIR, "assets", "sounds", f"{base_nome}.mp3"),
        os.path.join(BASE_DIR, "assets", "sounds", f"{base_nome}.wav"),
    ]
    for c in candidatos:
        if os.path.exists(c):
            return c

    # Se nenhum arquivo foi encontrado, gera um loop 8-bit padrão para não ficar mudo
    fallback_wav = os.path.join(AUDIO_DIR, f"{base_nome}.wav")
    if base_nome == "boss":
        notas = [146.83, 146.83, 174.61, 164.81, 130.81, 130.81, 146.83, 110.00]
    else:
        notas = [220.00, 261.63, 293.66, 329.63, 293.66, 261.63, 220.00, 196.00]
    _gerar_wav_loop_8bit(fallback_wav, notas)
    return fallback_wav


class GameplayScene(State):
    _musica_ativa = None

    def __init__(self, game, level_id=1, speedrun=False,
                 tempo_speedrun=0.0):
        super().__init__(game)
        self.level_id       = level_id
        self.speedrun       = speedrun
        self.tempo_speedrun = tempo_speedrun

    def _atualizar_musica(self):
        base_nome = "boss" if self.level_id >= 3 else "fases_1_2"
        alvo = _resolver_arquivo_musica(base_nome)

        if alvo == GameplayScene._musica_ativa and pygame.mixer.music.get_busy():
            return

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            pygame.mixer.music.stop()
            pygame.mixer.music.load(alvo)
            pygame.mixer.music.set_volume(0.6)
            pygame.mixer.music.play(-1)
            GameplayScene._musica_ativa = alvo
            print(f"[AUDIO] Tocando em loop: {alvo}")
        except pygame.error as e:
            print(f"[AUDIO ERRO] Falha ao tocar '{alvo}': {e}")

    def _carregar_fundo(self):
        caminho = self.cfg.get(
            "fundo",
            f"assets/images/backgrounds/level_{self.level_id}.png",
        )
        if not os.path.isabs(caminho):
            caminho = os.path.join(BASE_DIR, caminho)
        if not os.path.exists(caminho):
            return None

        img = pygame.image.load(caminho).convert()
        altura_area = max(1, HEIGHT - HUD_HEIGHT)
        return pygame.transform.scale(img, (WIDTH, altura_area))

    def enter(self, **kwargs):
        self.cfg           = LEVELS[self.level_id - 1]
        self.plataformas   = self.cfg["plataformas"]
        self.armadilhas    = [
            Armadilha(ax, ay, aw, ah)
            for (ax, ay, aw, ah) in self.cfg.get("armadilhas", [])
        ]
        self.fundo_img     = self._carregar_fundo()
        self.player        = Player(self.plataformas)
        self.inimigos      = [self._criar(t, x, y)
                              for (t, x, y) in self.cfg["inimigos"]]
        self.projeteis     = []
        self.tempo         = 0.0
        self.pontos        = 0
        self.tempo_nivel   = 0.0

        # Variáveis para a machadinha não disparar tudo de uma vez
        self._x_anterior = False
        self._z_anterior = False

        self._atualizar_musica()

    def _criar(self, tipo, x, y):
        return {
            "bat":      Morcego,
            "zombie":   Zumbi,
            "skeleton": Esqueleto,
            "boss":     LordeNayatuhen,
        }[tipo](x, y)

    def handle_input(self):
        kb = self.game.keyboard
        if kb.key_pressed("ESC"):
            from src.scenes.menu import MenuScene
            self.game.change_state(MenuScene(self.game))
            return

        # Edge detection para a machadinha (X ou Z)
        x_agora = kb.key_pressed("X")
        z_agora = kb.key_pressed("Z")

        # Só atira se apertou AGORA e NÃO estava apertado no frame anterior
        if (x_agora and not self._x_anterior) or (z_agora and not self._z_anterior):
            self.player.atirar_machado(self.projeteis)

        self._x_anterior = x_agora
        self._z_anterior = z_agora

    def _chegou_ao_fim_da_fase(self):
        # Na tela 3 (Sala do Trono), a vitória ocorre ao derrotar Lorde Nayatuhen
        if self.level_id >= 3:
            return len(self.inimigos) == 0

        chegou_direita = (self.player.x + self.player.width) >= (WIDTH - 8)
        return chegou_direita

    def update(self, dt):
        self.tempo += dt
        self.tempo_nivel += dt

        self.player.update(dt, self.game.keyboard, self.tempo)

        for inim in self.inimigos[:]:
            if not inim.vivo:
                self.pontos += inim.PONTOS
                self.inimigos.remove(inim)
                continue
            inim.update(dt, self.player, self.projeteis, self.tempo)

        for p in self.projeteis[:]:
            p.update(dt)
            if not p.vivo:
                self.projeteis.remove(p)

        self._colisoes()

        if self.player.vida <= 0:
            from src.scenes.game_over import GameOverScene
            self.game.change_state(GameOverScene(
                self.game, self.tempo_speedrun + self.tempo_nivel,
                self.speedrun))
            return

        if self._chegou_ao_fim_da_fase():
            acumulado = self.tempo_speedrun + self.tempo_nivel
            if self.level_id >= 3:
                from src.scenes.victory import VictoryScene
                self.game.change_state(VictoryScene(
                    self.game, acumulado, self.speedrun))
            else:
                self.game.change_state(GameplayScene(
                    self.game, self.level_id + 1,
                    speedrun=self.speedrun,
                    tempo_speedrun=acumulado))

    def _colisoes(self):
        self._whip_x_inimigos()
        self._whip_x_projeteis_parry()
        self._projeteis_x_player()
        self._projeteis_refletidos_x_inimigos()
        self._machado_x_inimigos()
        self._armadilhas_x_player()
        self._contato_x_player()

    def _whip_x_inimigos(self):
        wr = self.player.whip_rect()
        if not wr or self.player.whip_hit_esta_swing:
            return
        for inim in self.inimigos:
            if not inim.hitbox().colliderect(wr):
                continue
            if isinstance(inim, LordeNayatuhen):
                if not inim.guarda_aberta(self.tempo):
                    continue
                dano = BOSS_DANO_WHIP
                duracao_stun = 0.0
            else:
                dano = 1
                duracao_stun = 0.25 if isinstance(inim, (Zumbi, Esqueleto)) else 0.0
            inim.levar_dano(dano, tempo=self.tempo, duracao_stun=duracao_stun)
            self.player.whip_hit_esta_swing = True
            break

    def _whip_x_projeteis_parry(self):
        tip = self.player.whip_tip_rect()
        if not tip:
            return
        for p in self.projeteis:
            if p.refletido:
                continue
            if p.hitbox().colliderect(tip):
                p.refletir()
                for inim in self.inimigos:
                    if isinstance(inim, LordeNayatuhen):
                        inim.abrir_guarda(self.tempo)

    def _projeteis_x_player(self):
        for p in self.projeteis[:]:
            if p.refletido or p.tipo == "axe":
                continue
            if p.hitbox().colliderect(self.player.rect()):
                if self.player.levar_dano(self.tempo):
                    self.projeteis.remove(p)

    def _projeteis_refletidos_x_inimigos(self):
        for p in self.projeteis[:]:
            if not p.refletido:
                continue
            for inim in self.inimigos[:]:
                if not p.hitbox().colliderect(inim.hitbox()):
                    continue
                if isinstance(inim, LordeNayatuhen):
                    inim.levar_dano(BOSS_DANO_REFLETIDO)
                    inim.abrir_guarda(self.tempo)
                else:
                    inim.levar_dano(2)
                self.projeteis.remove(p)
                break

    def _machado_x_inimigos(self):
        for p in self.projeteis[:]:
            if p.tipo != "axe":
                continue
            for inim in self.inimigos[:]:
                if not p.hitbox().colliderect(inim.hitbox()):
                    continue
                if isinstance(inim, LordeNayatuhen):
                    if not inim.guarda_aberta(self.tempo):
                        continue
                    inim.levar_dano(1)
                else:
                    inim.levar_dano(2)
                self.projeteis.remove(p)
                break

    def _armadilhas_x_player(self):
        pr = self.player.rect()
        for trap in self.armadilhas:
            if pr.colliderect(trap.rect):
                self.player.levar_dano(self.tempo)

    def _contato_x_player(self):
        for inim in self.inimigos:
            if isinstance(inim, LordeNayatuhen):
                continue
            if inim.hitbox().colliderect(self.player.rect()):
                self.player.levar_dano(self.tempo)

    def draw(self):
        w = self.game.window
        w.set_background_color(COR_FUNDO)

        if self.fundo_img is not None:
            w.screen.blit(self.fundo_img, (0, HUD_HEIGHT))

        for (px, py, pw, ph) in self.plataformas:
            pygame.draw.rect(w.screen, COR_PLATAFORMA, (px, py, pw, ph))

        for trap in self.armadilhas:
            trap.draw(w)

        for inim in self.inimigos:
            inim.draw(w)

        for p in self.projeteis:
            p.draw(w.screen)
        self.player.draw_custom(w, self.tempo)

        if self.level_id == 3:
            boss = next((i for i in self.inimigos
                         if isinstance(i, LordeNayatuhen)), None)
            if boss:
                status = (
                    "GUARDA ABERTA! ATAQUE!"
                    if boss.guarda_aberta(self.tempo)
                    else "Ponta do chicote para PARRY e abrir a guarda"
                )
                cor_status = (
                    COR_DESTAQUE if boss.guarda_aberta(self.tempo)
                    else (190, 190, 210)
                )
                aviso = self.game.fonts["normal"].render(status, True, cor_status)
                w.screen.blit(aviso, (WIDTH // 2 - aviso.get_width() // 2, HUD_HEIGHT + 12))

        self._draw_hud()

    def _draw_hud(self):
        g = self.game
        w = g.window
        pygame.draw.rect(w.screen, COR_HUD, (0, 0, WIDTH, HUD_HEIGHT))
        pygame.draw.line(w.screen, (80, 80, 80),
                         (0, HUD_HEIGHT), (WIDTH, HUD_HEIGHT), 2)

        for i in range(self.player.vida_max):
            cor = COR_VIDA if i < self.player.vida else COR_VIDA_VAZIA
            pygame.draw.rect(w.screen, cor, (10 + i * 22, 14, 18, 30))
            pygame.draw.rect(w.screen, (0, 0, 0),
                             (10 + i * 22, 14, 18, 30), 2)

        s = g.fonts["normal"].render(
            f"Score: {self.pontos}", True, COR_TEXTO)
        w.screen.blit(s, (10, HUD_HEIGHT // 2 + 6))

        centro_x = WIDTH // 2
        pygame.draw.circle(w.screen, (180, 180, 100),
                           (centro_x - 60, 30), 12)
        t = g.fonts["normal"].render(
            f"x{self.player.axes}", True, COR_DESTAQUE)
        w.screen.blit(t, (centro_x - 30, 18))

        if self.level_id != 3:
            fase = g.fonts["normal"].render(
                self.cfg["nome"], True, (200, 200, 200))
            w.screen.blit(fase, (WIDTH - fase.get_width() - 20, 8))

        if self.speedrun:
            total = self.tempo_speedrun + self.tempo_nivel
            st = g.fonts["normal"].render(
                f"{total:06.2f}s", True, COR_DESTAQUE)
            w.screen.blit(st, (WIDTH - st.get_width() - 20,
                               HUD_HEIGHT // 2 + 6))

        if self.level_id == 3:
            boss = next((i for i in self.inimigos
                         if isinstance(i, LordeNayatuhen)), None)
            if boss:
                rotulo = g.fonts["normal"].render(
                    "LORDE NAYATU", True, COR_DESTAQUE)
                bw = 260
                bx = WIDTH - bw - 20
                by = HUD_HEIGHT // 2 - 4
                w.screen.blit(rotulo, (bx, 4))
                pygame.draw.rect(w.screen, COR_VIDA_VAZIA,
                                 (bx, by + 12, bw, 14))
                frac = max(0, boss.hp / boss.HP_INI)
                pygame.draw.rect(w.screen, COR_SANGRENTO,
                                 (bx, by + 12, int(bw * frac), 14))
                pygame.draw.rect(w.screen, (0, 0, 0),
                                 (bx, by + 12, bw, 14), 2)