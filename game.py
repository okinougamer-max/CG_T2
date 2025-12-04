import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import random
import math

import fundo
import menu

# ================= CONFIGURAÇÕES DO JOGO =================
COLS = 8
ROWS = 8
CELL_SIZE = 4.0 
GRID_Y_OFFSET = 5.0 

# ================= FUNÇÕES AUXILIARES =================
def desenhar_texto_hud(texto, x, y, display, cor=(255,255,255,255)):
    try:
        font = pygame.font.SysFont('arial', 32, bold=True)
    except:
        font = pygame.font.Font(None, 32)
    text_surface = font.render(texto, True, cor).convert_alpha()
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
    for i in range(COLS + 1):
        x = x_start + i * CELL_SIZE
        glVertex3f(x, GRID_Y_OFFSET, z_start)
        glVertex3f(x, GRID_Y_OFFSET, z_start + profundidade_total)
    
    for i in range(ROWS + 1):
        z = z_start + i * CELL_SIZE
        glVertex3f(x_start, GRID_Y_OFFSET, z)
        glVertex3f(x_start + largura_total, GRID_Y_OFFSET, z)
    glEnd()
    
    glEnable(GL_LIGHTING)
    glEnable(GL_TEXTURE_2D)

def get_world_pos(gx, gz):
    wx = (gx - (COLS-1)/2.0) * CELL_SIZE
    wz = (gz - (ROWS-1)/2.0) * CELL_SIZE 
    return wx, GRID_Y_OFFSET, wz

# ================= NOVO MODO: VISUALIZAR MAPA =================
def visualizar_mapa(display):
    """
    Modo de câmera livre para inspecionar o cenário.
    """
    clock = pygame.time.Clock()
    
    # Posição inicial da câmera
    cam_x = 0
    cam_y = 30
    cam_z = 60
    
    tempo_fundo = 0

    running = True
    while running:
        clock.tick(60)
        tempo_fundo += 0.5

        # --- INPUT ---
        for event in pygame.event.get():
            if event.type == QUIT:
                return False # Sai do programa todo
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return True # Volta para o menu

        # Controles contínuos da câmera
        keys = pygame.key.get_pressed()
        vel = 1.0
        
        # Move no plano X/Z
        if keys[K_LEFT]:  cam_x -= vel
        if keys[K_RIGHT]: cam_x += vel
        if keys[K_UP]:    cam_z -= vel
        if keys[K_DOWN]:  cam_z += vel
        
        # Zoom / Altitude
        if keys[K_w]: cam_y -= vel # Desce/Zoom In
        if keys[K_s]: cam_y += vel # Sobe/Zoom Out

        # Limites básicos para não perder a câmera
        cam_y = max(5, min(cam_y, 150))

        # --- DESENHO ---
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, (display[0]/display[1]), 0.1, 400.0) # Far clip maior
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # A câmera olha de (cam_x, cam_y, cam_z) para (cam_x, 0, cam_z - 30)
        # Isso cria um efeito de "arrastar" o mapa
        gluLookAt(cam_x, cam_y, cam_z, cam_x, 0, cam_z - 40, 0, 1, 0)

        # Desenha mundo
        fundo.desenhar_cenario(tempo_fundo)
        desenhar_grade() # Mostra a grade do jogo para referência

        # HUD de Instruções
        desenhar_texto_hud("MODO OBSERVADOR", 10, display[1] - 40, display, (0, 255, 255, 255))
        desenhar_texto_hud("Setas: Mover | W/S: Zoom | ESC: Menu", 10, 20, display, (200, 200, 200, 255))
        
        pygame.display.flip()

# ================= LOOP DO JOGO =================
def loop_jogo(display):
    # IDs de texturas
    tex_nave = None
    tex_meteoro = None
    for p in fundo.PLANETAS:
        if p["nome"] == "Terra": tex_nave = p["tex_id"]
        if p["nome"] == "Marte": tex_meteoro = p["tex_id"]

    ship_x = 4
    ship_z = 0
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

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False # Sai do app
            if event.type == pygame.KEYDOWN and game_state == "PLAYING":
                if event.key == pygame.K_ESCAPE: 
                    return True # Volta pro menu
                
                if event.key == pygame.K_LEFT and ship_x > 0: ship_x -= 1
                if event.key == pygame.K_RIGHT and ship_x < COLS - 1: ship_x += 1
                if event.key == pygame.K_UP and ship_z > 0: ship_z -= 1
                if event.key == pygame.K_DOWN and ship_z < ROWS - 1: ship_z += 1

        if game_state == "PLAYING":
            if time_left == 0: game_state = "WON"
            
            if current_ticks - last_meteor_time > meteor_spawn_interval:
                col_spawn = random.randint(0, COLS - 1)
                meteoros.append({'x': col_spawn, 'z': ROWS})
                last_meteor_time = current_ticks
            
            meteor_move_timer += dt
            if meteor_move_timer > meteor_move_interval:
                meteor_move_timer = 0
                for m in meteoros: m['z'] -= 1
                meteoros = [m for m in meteoros if m['z'] >= -1]
                
                for m in meteoros:
                    if m['x'] == ship_x and m['z'] == ship_z:
                        game_state = "LOST"

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, (display[0]/display[1]), 0.1, 200.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(0, 30, 50, 0, 0, 0, 0, 1, 0)

        fundo.desenhar_cenario(tempo_fundo)
        desenhar_grade()
        
        if game_state != "LOST" or (current_ticks % 500 < 250):
            nx, ny, nz = get_world_pos(ship_x, ship_z)
            glPushMatrix()
            glTranslate(nx, ny, nz)
            glTranslate(0, math.sin(tempo_fundo*0.1)*0.2, 0) 
            fundo.desenhar_esfera_texturizada(1.2, tex_nave)
            glPopMatrix()

        for m in meteoros:
            mx, my, mz = get_world_pos(m['x'], m['z'])
            glPushMatrix()
            glTranslate(mx, my, mz)
            fundo.desenhar_esfera_texturizada(1.0, tex_meteoro)
            glPopMatrix()

        if game_state == "PLAYING":
            desenhar_texto_hud(f"Tempo: {time_left}s", 10, display[1] - 40, display)
        elif game_state == "WON":
            desenhar_texto_hud("VITORIA!", display[0]//2 - 60, display[1]//2, display)
        elif game_state == "LOST":
            desenhar_texto_hud("GAME OVER", display[0]//2 - 80, display[1]//2, display)

        pygame.display.flip()

# ================= MAIN =================
def main():
    pygame.init()
    display = (1280, 720)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Space Dodge - 30 Segundos!")

    fundo.init_opengl()
    fundo.init_all_textures()

    while True:
        # Abre o Menu
        escolha = menu.executar(display)

        if escolha == "JOGAR":
            # Roda o Jogo. Se retornar False, fecha o app.
            if not loop_jogo(display):
                break
        
        elif escolha == "MAPA":
            # Roda o Mapa. Se retornar False, fecha o app.
            if not visualizar_mapa(display):
                break
        
        elif escolha is None:
            # Sair
            break

    pygame.quit()

if __name__ == "__main__":
    main()