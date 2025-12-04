import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import random
import math

# Importa o módulo de fundo
import fundo

# ================= CONFIGURAÇÕES DO JOGO =================
COLS = 5
ROWS = 8
CELL_SIZE = 4.0 
GRID_Y_OFFSET = 5.0 

def desenhar_texto_hud(texto, x, y, display):
    font = pygame.font.SysFont('arial', 32, bold=True)
    text_surface = font.render(texto, True, (255, 255, 255, 255)).convert_alpha()
    text_data = pygame.image.tostring(text_surface, "RGBA", True)
    w, h = text_surface.get_size()

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, display[0], 0, display[1])
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glRasterPos2d(x, y)
    glDrawPixels(w, h, GL_RGBA, GL_UNSIGNED_BYTE, text_data)
    glDisable(GL_BLEND)
    
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()

def desenhar_grade():
    glDisable(GL_TEXTURE_2D)
    glDisable(GL_LIGHTING)
    glColor3f(0.0, 1.0, 0.0)
    glLineWidth(1.0)
    
    largura_total = COLS * CELL_SIZE
    profundidade_total = ROWS * CELL_SIZE
    x_start = -largura_total / 2.0
    z_start = -profundidade_total / 2.0

    glBegin(GL_LINES)
    # Linhas verticais
    for i in range(COLS + 1):
        x = x_start + i * CELL_SIZE
        glVertex3f(x, GRID_Y_OFFSET, z_start)
        glVertex3f(x, GRID_Y_OFFSET, z_start + profundidade_total)
    
    # Linhas horizontais
    for i in range(ROWS + 1):
        z = z_start + i * CELL_SIZE
        glVertex3f(x_start, GRID_Y_OFFSET, z)
        glVertex3f(x_start + largura_total, GRID_Y_OFFSET, z)
    glEnd()
    
    glEnable(GL_LIGHTING)
    glEnable(GL_TEXTURE_2D)

def get_world_pos(gx, gz):
    """Converte coordenadas da grade (coluna, linha) para coordenadas 3D"""
    wx = (gx - (COLS-1)/2.0) * CELL_SIZE
    wz = (gz - (ROWS-1)/2.0) * CELL_SIZE 
    return wx, GRID_Y_OFFSET, wz

def main():
    pygame.init()
    largura, altura = 800, 600
    display = (largura, altura)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Space Dodge - 30 Segundos!")

    # Usa funções do fundo.py para configurar OpenGL
    fundo.init_opengl()
    fundo.init_all_textures()

    # IDs de texturas reutilizadas do fundo
    tex_nave = None
    tex_meteoro = None
    for p in fundo.PLANETAS:
        if p["nome"] == "Terra": tex_nave = p["tex_id"]
        if p["nome"] == "Marte": tex_meteoro = p["tex_id"]

    # Estado do Jogo
    ship_x = 2 # Coluna (0-4)
    ship_z = 0 # Linha (0-7)
    meteoros = []
    
    game_state = "PLAYING"
    start_ticks = pygame.time.get_ticks()
    last_meteor_time = 0
    meteor_spawn_interval = 800
    meteor_move_timer = 0
    meteor_move_interval = 200
    
    tempo_fundo = 0
    clock = pygame.time.Clock()

    while True:
        dt = clock.tick(60)
        tempo_fundo += 0.5
        
        current_ticks = pygame.time.get_ticks()
        elapsed_seconds = (current_ticks - start_ticks) / 1000.0
        time_left = max(0, 30 - int(elapsed_seconds))

        # --- INPUT ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); return
            if event.type == pygame.KEYDOWN and game_state == "PLAYING":
                if event.key == pygame.K_ESCAPE: pygame.quit(); return
                
                # Movimentação Horizontal
                if event.key == pygame.K_LEFT and ship_x > 0: ship_x -= 1
                if event.key == pygame.K_RIGHT and ship_x < COLS - 1: ship_x += 1
                
                # Movimentação Vertical (CORRIGIDO)
                # K_UP agora diminui o Z (vai para o fundo/cima da tela)
                if event.key == pygame.K_UP and ship_z > 0: ship_z -= 1
                # K_DOWN agora aumenta o Z (vem para frente/baixo da tela)
                if event.key == pygame.K_DOWN and ship_z < ROWS - 1: ship_z += 1

        # --- LÓGICA ---
        if game_state == "PLAYING":
            if time_left == 0:
                game_state = "WON"
            
            # Spawn Meteoros
            if current_ticks - last_meteor_time > meteor_spawn_interval:
                col_spawn = random.randint(0, COLS - 1)
                meteoros.append({'x': col_spawn, 'z': ROWS})
                last_meteor_time = current_ticks
            
            # Mover Meteoros
            meteor_move_timer += dt
            if meteor_move_timer > meteor_move_interval:
                meteor_move_timer = 0
                for m in meteoros: m['z'] -= 1
                meteoros = [m for m in meteoros if m['z'] >= -1]
                
                # Colisão
                for m in meteoros:
                    if m['x'] == ship_x and m['z'] == ship_z:
                        game_state = "LOST"

        # --- DESENHO ---
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Câmera
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, (display[0]/display[1]), 0.1, 200.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(0, 30, 50, 0, 0, 0, 0, 1, 0)

        # 1. Desenha o Fundo (Sistema Solar)
        fundo.desenhar_cenario(tempo_fundo)

        # 2. Desenha o Jogo
        desenhar_grade()
        
        # Nave
        if game_state != "LOST" or (current_ticks % 500 < 250):
            nx, ny, nz = get_world_pos(ship_x, ship_z)
            glPushMatrix()
            glTranslate(nx, ny, nz)
            # Leve flutuação
            glTranslate(0, math.sin(tempo_fundo*0.1)*0.2, 0) 
            fundo.desenhar_esfera_texturizada(1.2, tex_nave)
            glPopMatrix()

        # Meteoros
        for m in meteoros:
            mx, my, mz = get_world_pos(m['x'], m['z'])
            glPushMatrix()
            glTranslate(mx, my, mz)
            fundo.desenhar_esfera_texturizada(1.0, tex_meteoro)
            glPopMatrix()

        # 3. HUD
        if game_state == "PLAYING":
            desenhar_texto_hud(f"Tempo: {time_left}s", 10, altura - 40, display)
        elif game_state == "WON":
            desenhar_texto_hud("VITORIA!", largura//2 - 60, altura//2, display)
        elif game_state == "LOST":
            desenhar_texto_hud("GAME OVER", largura//2 - 80, altura//2, display)

        pygame.display.flip()

if __name__ == "__main__":
    main()