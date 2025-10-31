# Top-Down Shooter Game in Pygame
# Autor: Guilherme Oliveira
# Requisitos: Pygame instalado, pasta "assets" com imagens e sons necessários
# Descrição: Jogo simples de tiro com inimigos, asteroides, vida e fases de dificuldade.
# Controles: Setas/WASD para mover, Espaço para atirar, ESC para pausar.
# Instruções: Derrote 50 inimigos para vencer. Evite ser atingido por tiros inimigos e colidir com asteroides.
# Estrutura do código: Inicialização, carregamento de assets, loop principal com estados de jogo (intro, jogando, game over, vitória).
# Fonte: https://www.pygame.org/docs/ref/pygame.html / Documentação oficial do Pygame

import pygame
import random
import os
import sys

pygame.init()

# Configurações gerais da tela e jogo https://www.youtube.com/watch?v=Q-__8Xw9KTM
WIDTH, HEIGHT = 800, 600
FPS = 60
ASSET_DIR = "assets"

# Inicialização da Tela
screen = pygame.display.set_mode((WIDTH, HEIGHT)) #https://www.pygame.org/docs/ref/display.html
pygame.display.set_caption("Top-Down Shooter - Completo")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 28)
big_font = pygame.font.SysFont(None, 44)

# Funções auxiliares para carregar imagens e sons https://www.youtube.com/watch?v=jO6qQDNa2UY
def load_image(path, scale=None, alpha=True):
    try:
        img = pygame.image.load(path).convert_alpha() if alpha else pygame.image.load(path).convert()
        if scale:
            img = pygame.transform.scale(img, scale)
        return img # Retorna a imagem carregada 
    except Exception as e:
        print(f"Erro carregando {path}: {e}") # Retorna None em caso de erro
        return None

def load_sound(path): # Retorna o objeto Sound ou None
    try:
        return pygame.mixer.Sound(path)
    except Exception as e:
        print(f"Erro carregando {path}: {e}")
        return None

# Função para desenhar texto na tela
def draw_text(surf, text, x, y, color=(255,255,255), center=False, font_obj=None): # Função para desenhar texto na tela
    if font_obj is None:
        font_obj = font
    img = font_obj.render(text, True, color)
    if center:
        r = img.get_rect(center=(x,y))
        surf.blit(img, r)
    else:
        surf.blit(img, (x,y)) #https://stackoverflow.com/questions/48064934/pygame-screen-wont-fill-or-draw-text
        # Carregamento de assets (imagens e sons)
player_img = load_image(os.path.join(ASSET_DIR, "player.png"), scale=(50,50))
enemy_img = load_image(os.path.join(ASSET_DIR, "enemy.png"), scale=(50,50))
asteroid_img = load_image(os.path.join(ASSET_DIR, "asteroid.png"), scale=(48,48))
laser_img = load_image(os.path.join(ASSET_DIR, "laser.png"), scale=(10,20))
ship2_img = load_image(os.path.join(ASSET_DIR, "ship2.png"), scale=(480,240))

# Fundo único e estático 
bg_image = load_image(os.path.join(ASSET_DIR, "background.png"), scale=(WIDTH,HEIGHT), alpha=False)
if not bg_image:
    bg_image = pygame.Surface((WIDTH, HEIGHT))
    bg_image.fill((10, 10, 30))

# Tela de vitória e derrota
congrats_img = load_image(os.path.join(ASSET_DIR, "congrats.png"), scale=(WIDTH,HEIGHT), alpha=False)
gameover_img = load_image(os.path.join(ASSET_DIR, "gameover.png"), scale=(WIDTH,HEIGHT), alpha=False)
hp_img = load_image(os.path.join(ASSET_DIR, "hp.png"))
btn_start_img = load_image(os.path.join(ASSET_DIR, "button.png"))
btn_big_img = load_image(os.path.join(ASSET_DIR, "buttons.png"))

# Sons do jogo 
shoot_sound = load_sound(os.path.join(ASSET_DIR, "laser2.ogg"))
hit_sound = load_sound(os.path.join(ASSET_DIR, "hit.wav"))
lose_sound = load_sound(os.path.join(ASSET_DIR, "lose.ogg"))
victory_sound = load_sound(os.path.join(ASSET_DIR, "victory.ogg"))  # 🔊 novo som de vitória

# Estado do jogo
game_state = "intro"
player_w, player_h = (50,50) # Tamanho padrão do jogador
if player_img:
    player_w, player_h = player_img.get_width(), player_img.get_height()
    
   # Rect do player define posição e tamanho
player = pygame.Rect(WIDTH//2 - player_w//2, HEIGHT - player_h - 50, player_w, player_h) # Retângulo do jogador
player_speed = 5 # Velocidade do jogador
player_hp = 100 # Vida do jogador
max_hp = 100

#Listas para projetéis e inimigos
player_projectiles = [] # projetéis do jogador
enemy_projectiles = [] 
shoot_cooldown = 0 # Controle de velocidade de tiro
enemies_defeated = 0

inimigos = []
asteroids = []
spawn_cooldown = 0
asteroid_cooldown = 0

# Fases de dificuldade
phase_defs = [
    {"enemy_speed": 2, "spawn": 70, "enemy_shoot_cd": 120}, # Fase 1
    {"enemy_speed": 2, "spawn": 60, "enemy_shoot_cd": 110}, # Fase 2
    {"enemy_speed": 3, "spawn": 50, "enemy_shoot_cd": 100}, # Fase 3
]

def get_phase_by_kills(kills): # Retorna o índice da fase baseado no número de inimigos abatidos
    if kills <= 20: return 0
    if kills <= 35: return 1
    return 2

def make_enemy_rect(x,y):
    if enemy_img:
        return pygame.Rect(x,y, enemy_img.get_width(), enemy_img.get_height()) # Retorna rect baseado na imagem do inimigo na posição x,y
    return pygame.Rect(x,y,50,50)

def make_asteroid_rect(x,y):
    if asteroid_img:
        return pygame.Rect(x,y, asteroid_img.get_width(), asteroid_img.get_height()) # Retorna rect baseado na imagem do asteroide na posição x,y
    return pygame.Rect(x,y,48,48)

#Reseta todas as variáveis do jogo para iniciar uma nova partida
def reset_game():
    global player, player_hp, player_projectiles, enemy_projectiles
    global inimigos, asteroids, spawn_cooldown, asteroid_cooldown
    global enemies_defeated, shoot_cooldown
    player.x = WIDTH//2 - player_w//2; player.y = HEIGHT - player_h -50
    player_hp = max_hp
    player_projectiles.clear(); enemy_projectiles.clear()
    inimigos.clear(); asteroids.clear()
    spawn_cooldown = asteroid_cooldown = 0
    enemies_defeated = 0; shoot_cooldown=0

# Loop principal
running = True
victory_sound_played = False  # 🔊 Evita tocar som de vitória repetidamente

while running:
    dt = clock.tick(FPS) # Controla o FPS mantendo o jogo rodando a 60 quadros por segundo
    mx,my = pygame.mouse.get_pos()
    mouse_clicked = False
    
    # ---- EVENTOS ----
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT: running=False
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1: mouse_clicked=True
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE and game_state=="playing": game_state="menu"
    keys = pygame.key.get_pressed() # Teclas pressionadas

    # ---- INTRO ----
    if game_state=="intro":
        screen.fill((0,0,0))
        victory_sound_played = False  # resetar som da vitória ao reiniciar
        if ship2_img: screen.blit(ship2_img, (WIDTH//2-ship2_img.get_width()//2,80))
        draw_text(screen,"Missão: Derrote 50 inimigos e salve a galáxia!",WIDTH//2,360,center=True)
        
         # Botão continuar
        cont_rect = pygame.Rect(WIDTH//2-120,460,240,64)
        if btn_start_img:
            s = pygame.transform.scale(btn_start_img,(cont_rect.width,cont_rect.height))
            screen.blit(s,(cont_rect.x,cont_rect.y))
            draw_text(screen,"CONTINUAR",cont_rect.centerx,cont_rect.centery,center=True)
        else:
            pygame.draw.rect(screen,(40,40,40),cont_rect)
            draw_text(screen,"CONTINUAR",cont_rect.centerx,cont_rect.centery,center=True)
        if mouse_clicked and cont_rect.collidepoint((mx,my)):
            reset_game(); game_state="playing"

    #  PLAYING
    elif game_state=="playing":
        if player_hp <= 0:
            game_state="gameover"
            continue

        phase_index = get_phase_by_kills(enemies_defeated)
        phase = phase_defs[phase_index]

        # Movimentação do jogador
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: player.x-=player_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: player.x+=player_speed
        if keys[pygame.K_UP] or keys[pygame.K_w]: player.y-=player_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: player.y+=player_speed
        player.x = max(0,min(WIDTH-player.width,player.x))
        player.y = max(0,min(HEIGHT-player.height,player.y))

        # Tiro do jogador
        if shoot_cooldown>0: shoot_cooldown-=1
        if keys[pygame.K_SPACE] and shoot_cooldown==0:
            lw,lh = (10,20)
            if laser_img: lw,lh = laser_img.get_width(), laser_img.get_height()
            proj = pygame.Rect(player.centerx-lw//2,player.y,lw,lh)
            player_projectiles.append(proj)
            if shoot_sound:
                try: shoot_sound.play()
                except: pass
            shoot_cooldown=14

        # Atualiza posição dos projéteis do jogador
        for p in player_projectiles[:]:
            p.y-=12
            if p.y+p.height<0: player_projectiles.remove(p)

        # Spawn inimigos
        if spawn_cooldown<=0:
            ex = random.randint(0, WIDTH-60)
            inimigos.append(make_enemy_rect(ex,-60))
            spawn_cooldown = phase["spawn"]
        else: spawn_cooldown-=1

        # Spawn asteroides
        if asteroid_cooldown<=0:
            ax = random.randint(0, WIDTH-60)
            asteroids.append(make_asteroid_rect(ax,-60))
            asteroid_cooldown=110
        else: asteroid_cooldown-=1

        # Atualiza inimigos 
        for e in inimigos[:]:
            e.y += phase["enemy_speed"]
            if e.y>HEIGHT+80: inimigos.remove(e)
        # Inimigos atiram aleatoriamente
            if random.randint(0, phase["enemy_shoot_cd"]) == 0:
                lw,lh = (10,20)
                if laser_img: lw,lh = laser_img.get_width(), laser_img.get_height()
                proj = pygame.Rect(e.centerx-lw//2, e.bottom, lw, lh)
                proj_dx = (player.centerx - proj.centerx)/60
                proj_dy = 6
                enemy_projectiles.append({"rect":proj,"dx":proj_dx,"dy":proj_dy})
                if shoot_sound:
                    try: shoot_sound.play()
                    except: pass

        # Atualiza asteroides
        for a in asteroids[:]:
            a.y+=int(phase["enemy_speed"]*1.4)+1
            if a.y>HEIGHT+80: asteroids.remove(a)

        # Atualiza projéteis inimigos
        for ep in enemy_projectiles[:]:
            ep["rect"].x += ep["dx"]
            ep["rect"].y += ep["dy"]
            if ep["rect"].y>HEIGHT or ep["rect"].x<0 or ep["rect"].x>WIDTH:
                enemy_projectiles.remove(ep)

        # Colisões
        # Player projéteis -> inimigos/asteroides
        for e in inimigos[:]:
            for p in player_projectiles[:]:
                if e.colliderect(p):
                    inimigos.remove(e); player_projectiles.remove(p); enemies_defeated+=1; break

        for a in asteroids[:]:
            for p in player_projectiles[:]:
                if a.colliderect(p):
                    asteroids.remove(a); player_projectiles.remove(p); break

        #Projetéis inimigos -> player
        for ep in enemy_projectiles[:]:
            if player.colliderect(ep["rect"]):
                enemy_projectiles.remove(ep)
                player_hp -= 10
                if hit_sound: 
                    try: hit_sound.play()
                    except: pass
                if player_hp<=0:
                    if lose_sound: 
                        try: lose_sound.play()
                        except: pass
                    game_state="gameover"
                    break
        if game_state=="gameover": continue

        # Colisão player -> inimigos/asteroides
        for e in inimigos[:]:
            if player.colliderect(e):
                inimigos.remove(e); player_hp-=10
                if hit_sound: 
                    try: hit_sound.play()
                    except: pass
                if player_hp<=0:
                    if lose_sound: 
                        try: lose_sound.play()
                        except: pass
                    game_state="gameover"
                    break
        if game_state=="gameover": continue

        for a in asteroids[:]:
            if player.colliderect(a):
                asteroids.remove(a); player_hp-=15
                if hit_sound: 
                    try: hit_sound.play()
                    except: pass
                if player_hp<=0:
                    if lose_sound:
                        try: lose_sound.play()
                        except: pass
                    game_state="gameover"
                    break
        if game_state=="gameover": continue

        # Desenho dos elementos
        screen.blit(bg_image, (0, 0))
        if player_img: screen.blit(player_img,(player.x,player.y))
        else: pygame.draw.rect(screen,(200,60,60),player)

        for e in inimigos:
            if enemy_img: screen.blit(enemy_img,(e.x,e.y))
            else: pygame.draw.rect(screen,(0,200,0),e)

        for a in asteroids:
            if asteroid_img: screen.blit(asteroid_img,(a.x,a.y))
            else: pygame.draw.circle(screen,(120,120,120),(a.x+24,a.y+24),24)

        for p in player_projectiles:
            if laser_img: screen.blit(laser_img,(p.x,p.y))
            else: pygame.draw.rect(screen,(255,255,0),p)

        for ep in enemy_projectiles:
            if laser_img: screen.blit(laser_img,(ep["rect"].x,ep["rect"].y))
            else: pygame.draw.rect(screen,(255,0,0),ep["rect"])

        # HP e kills
        if hp_img:
            hp_w = int(hp_img.get_width() * player_hp / max_hp)
            hp_surf = hp_img.subsurface((0,0,hp_w,hp_img.get_height()))
            screen.blit(hp_surf,(10,10))
        else:
            pygame.draw.rect(screen,(255,0,0),(10,10,player_hp*2,20))

        # Draw kills
        draw_text(screen,f"Inimigos abatidos: {enemies_defeated}", WIDTH-220, 10)

        # Victory check
        if enemies_defeated>=50:
            game_state="victory"

    # GAME OVER 
    elif game_state=="gameover":
        if gameover_img:
            screen.blit(gameover_img, (0,0))
        else:
            screen.fill((0,0,0))

        restart_rect = pygame.Rect(WIDTH//2-100, HEIGHT//2+30, 200, 50)
        if btn_big_img:
            s = pygame.transform.scale(btn_big_img,(restart_rect.width,restart_rect.height))
            screen.blit(s,(restart_rect.x,restart_rect.y))
        pygame.draw.rect(screen,(150,40,40),restart_rect,2)
        draw_text(screen,"RESTART", restart_rect.centerx, restart_rect.centery, center=True)
        if mouse_clicked and restart_rect.collidepoint((mx,my)):
            reset_game()
            game_state="intro"

    # VITÓRIA
    elif game_state=="victory":
        # 🔊 toca o som de vitória uma única vez
        if not victory_sound_played and victory_sound:
            try:
                victory_sound.play()
            except:
                pass
            victory_sound_played = True

        if congrats_img:
            screen.blit(congrats_img,(0,0))
        draw_text(screen,"PARABÉNS! A GALÁXIA ESTÁ EM PAZ!", WIDTH//2, HEIGHT-120, center=True, font_obj=big_font)
        restart_rect = pygame.Rect(WIDTH//2-100, HEIGHT-80, 200, 50)
        if btn_big_img:
            s = pygame.transform.scale(btn_big_img,(restart_rect.width,restart_rect.height))
            screen.blit(s,(restart_rect.x,restart_rect.y))
        pygame.draw.rect(screen,(60,200,60),restart_rect,2)
        draw_text(screen,"RESTART", restart_rect.centerx, restart_rect.centery, center=True)
        if mouse_clicked and restart_rect.collidepoint((mx,my)):
            reset_game()
            game_state="intro"

    pygame.display.flip() # Atualiza a tela

pygame.quit() 
sys.exit() # Fecha o programa
