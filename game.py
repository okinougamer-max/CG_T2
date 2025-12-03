# game.py
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import random

# Importa o módulo de fundo (certifique-se de que fundo.py está na mesma pasta)
import fundo 

def draw_2d_rect(x, y, w, h, color):
    """Desenha um retângulo simples em 2D"""
    glDisable(GL_TEXTURE_2D)
    glColor3f(*color)
    glBegin(GL_QUADS)
    glVertex2f(x, y)
    glVertex2f(x + w, y)
    glVertex2f(x + w, y + h)
    glVertex2f(x, y + h)
    glEnd()

def render_text(text, font, x, y):
    """Renderiza texto na tela OpenGL (CORRIGIDO: Orientação Vertical)"""
    # Renderiza o texto em uma Surface do Pygame
    text_surface = font.render(text, True, (255, 255, 255, 255))
    
    # Converte para dados de textura (flipped=True para alinhar com a origem do GL no canto inferior)
    text_data = pygame.image.tostring(text_surface, "RGBA", True)
    w, h = text_surface.get_size()
    
    # Cria a textura no OpenGL
    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, text_data)
    
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor3f(1, 1, 1) # Garante que o texto seja branco
    
    # Desenha o quadrado com a textura do texto
    glBegin(GL_QUADS)
    # Correção: (0,0) da textura alinhado com (x,y) da tela (canto inferior esquerdo)
    glTexCoord2f(0, 0); glVertex2f(x, y)
    glTexCoord2f(1, 0); glVertex2f(x + w, y)
    glTexCoord2f(1, 1); glVertex2f(x + w, y + h)
    glTexCoord2f(0, 1); glVertex2f(x, y + h)
    glEnd()
    
    glDisable(GL_BLEND)
    glDisable(GL_TEXTURE_2D)
    glDeleteTextures(1, [tex_id])

def main():
    pygame.init()
    LARGURA, ALTURA = 1280, 720
    screen = pygame.display.set_mode((LARGURA, ALTURA), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Jogo Drop & Catch no Espaço")

    # --- Configuração 3D (Inicializa usando o fundo.py) ---
    fundo.init_opengl()
    fundo.init_all_textures()

    # --- Variáveis do Jogo ---
    font = pygame.font.SysFont('Arial', 32, bold=True)
    font_big = pygame.font.SysFont('Arial', 64, bold=True)
    
    player_w, player_h = 100, 20
    player_x = LARGURA // 2 - player_w // 2
    player_y = 50
    player_vel = 12
    
    estrelas = []
    spawn_timer = 0
    score = 0
    
    start_ticks = pygame.time.get_ticks()
    tempo_total = 30 # segundos
    game_over = False
    
    tempo_fundo = 0 # Variável para animação dos planetas
    clock = pygame.time.Clock()

    running = True
    while running:
        dt = clock.tick(60)
        
        # 1. Controle de Tempo
        segundos_passados = (pygame.time.get_ticks() - start_ticks) / 1000
        tempo_restante = max(0, tempo_total - segundos_passados)
        
        if tempo_restante <= 0:
            game_over = True

        # 2. Eventos
        for event in pygame.event.get():
            if event.type == QUIT: running = False
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE: running = False
                if event.key == K_r and game_over:
                    # Reiniciar Jogo
                    game_over = False
                    score = 0
                    estrelas = []
                    start_ticks = pygame.time.get_ticks()
                    player_x = LARGURA // 2 - player_w // 2

        # 3. Lógica (se não for Game Over)
        if not game_over:
            keys = pygame.key.get_pressed()
            if keys[K_LEFT] and player_x > 0: player_x -= player_vel
            if keys[K_RIGHT] and player_x < LARGURA - player_w: player_x += player_vel
            
            spawn_timer += 1
            if spawn_timer > 15: # Spawna estrela a cada ~15 frames
                spawn_timer = 0
                estrelas.append({'x': random.randint(0, LARGURA-30), 'y': ALTURA, 'w': 30, 'h': 30, 'vel': random.randint(4, 9)})
            
            # Movimento e Colisão
            player_rect = pygame.Rect(player_x, player_y, player_w, player_h)
            for e in estrelas[:]:
                e['y'] -= e['vel']
                # Remove se sair da tela
                if e['y'] < 0: 
                    estrelas.remove(e)
                # Checa colisão
                elif player_rect.colliderect(pygame.Rect(e['x'], e['y'], e['w'], e['h'])):
                    score += 1
                    estrelas.remove(e)

        # 4. RENDERIZAÇÃO
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # --- CAMADA 1: Fundo 3D (Sistema Solar) ---
        glMatrixMode(GL_PROJECTION); glLoadIdentity()
        gluPerspective(45, (LARGURA/ALTURA), 0.1, 200.0)
        glMatrixMode(GL_MODELVIEW); glLoadIdentity()
        gluLookAt(0, 40, 60, 0, 0, 0, 0, 1, 0)
        
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        
        # Chama a função de desenho do fundo.py
        tempo_fundo += 0.5
        fundo.desenhar_sistema_solar(tempo_fundo)

        # --- CAMADA 2: Interface 2D (Jogo) ---
        glMatrixMode(GL_PROJECTION); glLoadIdentity()
        gluOrtho2D(0, LARGURA, 0, ALTURA) # 0,0 é canto inferior esquerdo
        glMatrixMode(GL_MODELVIEW); glLoadIdentity()
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)

        # Desenha Jogador (Verde Neon)
        draw_2d_rect(player_x, player_y, player_w, player_h, (0.2, 1.0, 0.2))

        # Desenha Estrelas (Amarelo)
        for e in estrelas:
            draw_2d_rect(e['x'], e['y'], e['w'], e['h'], (1.0, 0.9, 0.1))

        # HUD (Texto)
        render_text(f"Score: {score}", font, 20, ALTURA - 40)
        render_text(f"Tempo: {tempo_restante:.1f}s", font, 20, ALTURA - 80)

        if game_over:
            render_text("FIM DE JOGO", font_big, LARGURA//2 - 180, ALTURA//2 + 20)
            render_text(f"Score Final: {score}", font, LARGURA//2 - 90, ALTURA//2 - 40)
            render_text("Pressione [R] para Reiniciar", font, LARGURA//2 - 170, ALTURA//2 - 90)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()