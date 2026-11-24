import pygame
from PPlay.sprite import Sprite
from src.config import (
    WIDTH, GRAVITY, PLAYER_SPEED, JUMP_FORCE, FLOOR_Y,
    PLAYER_HP, INVULN_TIME, AXES_INICIAIS,
    WHIP_WINDUP, WHIP_ACTIVE, WHIP_COOLDOWN,
    WHIP_RANGE, WHIP_TIP_FRACTION,
    CROUCH_HEIGHT_FACTOR,
)
from src.entities.projectile import Projectile


class Player:
    WHIP_NUM_FRAMES = 3
    SCALE = 2

    def __init__(self, plataformas):
        self.plataformas = plataformas

        self.anims = {
            "parado":   Sprite("assets/images/player/parado.png", 1),
            "andando":  Sprite("assets/images/player/andando.png", 3),
            "atacando": Sprite("assets/images/player/atacando.png", self.WHIP_NUM_FRAMES),
            "agachado": Sprite("assets/images/player/agachado.png", 1),
        }

        self.anims["andando"].set_total_duration(400)
        self.anims["atacando"].stop()

        self.anim_atual = "parado"
        self.width = self.anims["parado"].width * self.SCALE
        self.height = self.anims["parado"].height * self.SCALE

        self.reset()

    def reset(self):
        self.x = 100
        self.y = 0
        self.vx = 0
        self.vy = 0
        self.facing = 1
        self.no_chao = False
        self.agachado = False
        self.vida = PLAYER_HP
        self.vida_max = PLAYER_HP
        self.axes = AXES_INICIAIS
        self.invuln_ate = 0.0
        self.whip_state = "idle"
        self.whip_timer = 0.0
        self.whip_hit_esta_swing = False
        self.y = self.plataformas[0][1] - self.height
        self.anim_atual = "parado"

        self.anims["atacando"].set_curr_frame(0)
        self.anims["atacando"].stop()

        # Variável para guardar o estado do botão no frame anterior
        self._space_anterior = False

    def rect(self):
        if self.agachado and self.no_chao:
            h = int(self.height * CROUCH_HEIGHT_FACTOR)
            return pygame.Rect(int(self.x), int(self.y + self.height - h), self.width, h)
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def esta_atacando(self):
        return self.whip_state != "idle"

    def update(self, dt, keyboard, tempo):
        self._update_movimento(dt, keyboard)
        self._update_chicote(dt, keyboard)
        self._update_animacao()

    def _update_movimento(self, dt, keyboard):
        if self.esta_atacando():
            # Bloqueia movimento lateral, pulo e agachar durante toda a animação do chicote
            self.vx = 0
            if self.no_chao:
                self.agachado = False
        elif self.no_chao:
            self.agachado = keyboard.key_pressed("DOWN")
            if self.agachado:
                self.vx = 0
            elif keyboard.key_pressed("LEFT"):
                self.vx = -PLAYER_SPEED
                self.facing = -1
            elif keyboard.key_pressed("RIGHT"):
                self.vx = PLAYER_SPEED
                self.facing = 1
            else:
                self.vx = 0

            if keyboard.key_pressed("UP") and not self.agachado:
                self.vy = -JUMP_FORCE
                self.no_chao = False

        self.vy += GRAVITY * dt

        # Movimento horizontal
        self.x += self.vx * dt
        self.x = max(0, min(self.x, WIDTH - self.width))

        # Movimento vertical e colisões por baixo / por cima nas plataformas
        y_anterior = self.y
        self.y += self.vy * dt
        self.no_chao = False

        pr = pygame.Rect(int(self.x), int(self.y), self.width, self.height)

        # Colisão por baixo (subindo: self.vy < 0) em plataformas elevadas
        if self.vy < 0:
            for (px, py, pw, ph) in self.plataformas:
                if py >= FLOOR_Y:
                    continue
                plat = pygame.Rect(px, py, pw, ph)
                sobrepoe_x = pr.right > plat.left and pr.left < plat.right
                batendo_embaixo = (
                    sobrepoe_x
                    and (y_anterior + self.height >= plat.bottom or y_anterior >= plat.bottom - 12)
                    and pr.top <= plat.bottom
                    and pr.bottom > plat.bottom
                )
                if batendo_embaixo:
                    self.y = plat.bottom
                    self.vy = 0
                    pr.y = int(self.y)
                    break

        # Colisão por cima (caindo ou parado: self.vy >= 0)
        if self.vy >= 0:
            for (px, py, pw, ph) in self.plataformas:
                plat = pygame.Rect(px, py, pw, ph)
                if (pr.bottom >= plat.top and pr.bottom <= plat.top + 30
                        and pr.right > plat.left and pr.left < plat.right):
                    self.y = plat.top - self.height
                    self.vy = 0
                    self.no_chao = True
                    break

    def _iniciar_chicote(self):
        self.whip_state = "windup"
        self.whip_timer = 0.0
        self.whip_hit_esta_swing = False
        self.anims["atacando"].set_curr_frame(0)
        self.anims["atacando"].stop()

    def _sincronizar_frame_chicote(self):
        anim_atk = self.anims["atacando"]
        if self.whip_state == "idle":
            anim_atk.set_curr_frame(0)
        elif self.whip_state == "windup":
            anim_atk.set_curr_frame(0)
        elif self.whip_state == "active":
            # Primeira metade do active = frame 1; segunda metade = frame 2 (último frame)
            metade = WHIP_ACTIVE * 0.5
            frame = 1 if self.whip_timer < metade else self.WHIP_NUM_FRAMES - 1
            anim_atk.set_curr_frame(frame)
        elif self.whip_state == "cooldown":
            anim_atk.set_curr_frame(self.WHIP_NUM_FRAMES - 1)

    def _update_chicote(self, dt, keyboard):
        # Lógica de Edge Detection para o Espaço
        space_agora = keyboard.key_pressed("SPACE")

        if self.whip_state == "idle":
            if space_agora and not self._space_anterior:
                self._iniciar_chicote()
        elif self.whip_state == "windup":
            self.whip_timer += dt
            if self.whip_timer >= WHIP_WINDUP:
                self.whip_state = "active"
                self.whip_timer = 0.0
        elif self.whip_state == "active":
            self.whip_timer += dt
            if self.whip_timer >= WHIP_ACTIVE:
                self.whip_state = "cooldown"
                self.whip_timer = 0.0
        elif self.whip_state == "cooldown":
            self.whip_timer += dt
            if self.whip_timer >= WHIP_COOLDOWN:
                self.whip_state = "idle"
                self.whip_timer = 0.0

        self._sincronizar_frame_chicote()
        self._space_anterior = space_agora

    def _update_animacao(self):
        if self.whip_state in ["windup", "active", "cooldown"]:
            self.anim_atual = "atacando"
        elif not self.no_chao:
            self.anim_atual = "parado"
        elif self.agachado:
            self.anim_atual = "agachado"
        elif self.vx != 0:
            self.anim_atual = "andando"
        else:
            self.anim_atual = "parado"

    def _chicote_no_ultimo_frame(self):
        anim_atk = self.anims["atacando"]
        return (
            self.whip_state == "active"
            and anim_atk.get_curr_frame() == self.WHIP_NUM_FRAMES - 1
        )

    def whip_rect(self):
        if not self._chicote_no_ultimo_frame():
            return None
        altura_box = 36
        y = int(self.y + self.height // 2 - altura_box // 2)
        if self.facing == 1:
            return pygame.Rect(int(self.x + self.width * 0.5), y, WHIP_RANGE, altura_box)
        return pygame.Rect(int(self.x + self.width * 0.5 - WHIP_RANGE), y, WHIP_RANGE, altura_box)

    def whip_tip_rect(self):
        if not self._chicote_no_ultimo_frame():
            return None
        tip_w = max(12, int(WHIP_RANGE * WHIP_TIP_FRACTION))
        altura_box = 36
        y = int(self.y + self.height // 2 - altura_box // 2)
        if self.facing == 1:
            return pygame.Rect(
                int(self.x + self.width * 0.5 + WHIP_RANGE - tip_w),
                y,
                tip_w,
                altura_box,
            )
        return pygame.Rect(int(self.x + self.width * 0.5 - WHIP_RANGE), y, tip_w, altura_box)

    def atirar_machado(self, projeteis):
        if self.axes <= 0 or self.whip_state != "idle":
            return
        projeteis.append(
            Projectile("axe", self.x + self.width // 2, self.y + self.height // 3, self.facing)
        )
        self.axes -= 1

    def levar_dano(self, tempo):
        if self.invuln_ate > tempo:
            return False
        self.vida -= 1
        self.invuln_ate = tempo + INVULN_TIME
        return True

    def esta_invulneravel(self, tempo):
        return self.invuln_ate > tempo

    def draw_custom(self, window, tempo):
        if self.esta_invulneravel(tempo) and int(tempo * 15) % 2 == 0:
            return

        sprite_atual = self.anims[self.anim_atual]
        sprite_atual.x = self.x
        sprite_atual.y = self.y

        if self.anim_atual != "atacando":
            sprite_atual.play()
            sprite_atual.update()

        fw, fh = sprite_atual.width, sprite_atual.height
        num_frames = max(1, sprite_atual.image.get_width() // max(1, fw))
        frame_idx = max(0, min(sprite_atual.get_curr_frame(), num_frames - 1))
        frame_x = frame_idx * fw

        surf_frame = sprite_atual.image.subsurface(pygame.Rect(frame_x, 0, fw, fh))
        draw_w = fw * self.SCALE
        draw_h = fh * self.SCALE
        surf_scaled = pygame.transform.scale(surf_frame, (draw_w, draw_h))

        if self.facing == -1:
            surf_scaled = pygame.transform.flip(surf_scaled, True, False)

        # Mantém a base (pés) alinhada ao piso da hitbox mesmo se o frame tiver altura diferente
        draw_x = int(self.x)
        draw_y = int(self.y + self.height - draw_h)
        window.screen.blit(surf_scaled, (draw_x, draw_y))