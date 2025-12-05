import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import random
import math

import fundo
import menu

COLS = 8
ROWS = 8
CELL_SIZE = 4.0 
GRID_Y_OFFSET = 5.0 

def desenhar_texto_hud(texto, x, y, display, cor=(255,255,255,255), tamanho=32):
    try:
        font = pygame.font.SysFont('arial', tamanho, bold=True)
    except:
        font = pygame.font.Font(None, tamanho)
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
    
    glDisable(GL_DEPTH_TEST) 
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    glRasterPos2d(x, y)
    glDrawPixels(w, h, GL_RGBA, GL_UNSIGNED_BYTE, text_data)
    
    glDisable(GL_BLEND)
    glEnable(GL_DEPTH_TEST)
    
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

def get_world_pos(gx, gz):
    """Converte coordenadas da grade (0..7) para Mundo 3D."""
    wx = (gx - (COLS-1)/2.0) * CELL_SIZE
    wz = (gz - (ROWS-1)/2.0) * CELL_SIZE 
    return wx, GRID_Y_OFFSET, wz

def desenhar_nave_triangulo(texture_id=None):
    if texture_id:
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glColor3f(1.0, 1.0, 1.0) 
    else:
        glDisable(GL_TEXTURE_2D)
        glColor3f(0.0, 1.0, 1.0) 
    
    glBegin(GL_TRIANGLES)
    
    glNormal3f(0, 1, 0)
    if texture_id: glTexCoord2f(0.5, 1.0)
    glVertex3f(0.0, 0.0, -1.5)
    
    glNormal3f(0, 1, 0)
    if texture_id: glTexCoord2f(0.0, 0.0)
    glVertex3f(-1.0, 0.0, 1.5)
    
    glNormal3f(0, 1, 0)
    if texture_id: glTexCoord2f(1.0, 0.0)
    glVertex3f(1.0, 0.0, 1.5)
    
    glEnd()
    glDisable(GL_TEXTURE_2D)

def visualizar_mapa(display):
    clock = pygame.time.Clock()
    cam_x, cam_y, cam_z = 0, 30, 60
    tempo_fundo = 0

    running = True
    while running:
        clock.tick(60)
        tempo_fundo += 0.5

        for event in pygame.event.get():
            if event.type == QUIT: return False 
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE: return True 

        keys = pygame.key.get_pressed()
        if keys[K_LEFT]:  cam_x -= 1
        if keys[K_RIGHT]: cam_x += 1
        if keys[K_UP]:    cam_z -= 1
        if keys[K_DOWN]:  cam_z += 1
        if keys[K_w]: cam_y -= 1 
        if keys[K_s]: cam_y += 1 

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, (display[0]/display[1]), 0.1, 400.0) 
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(cam_x, cam_y, cam_z, cam_x, 0, cam_z - 40, 0, 1, 0)

        fundo.desenhar_cenario(tempo_fundo)
        
        desenhar_grade() 
        
        desenhar_texto_hud("MODO OBSERVADOR", 10, display[1] - 40, display, (0, 255, 255, 255))
        desenhar_texto_hud("Setas: Mover | W/S: Zoom | ESC: Menu", 10, 20, display, (200, 200, 200, 255))
        pygame.display.flip()

def loop_jogo(display, duracao_segundos, nivel):
    tex_meteoro = fundo.METEORO_CFG["tex_id"]
    tex_nave = fundo.NAVE_CFG["tex_id"]

    while True:
        ship_x, ship_z = 4, 0
        meteoros = []
        game_state = "PLAYING"
        start_ticks = pygame.time.get_ticks()
        last_meteor_time = 0
        
        meteor_spawn_interval = 800 if nivel < 3 else 400
        meteor_move_interval = 200
        meteor_move_timer = 0
        
        tempo_fundo = 0
        clock = pygame.time.Clock()
        restarting = False 

        while True:
            dt = clock.tick(60)
            tempo_fundo += 0.5
            current_ticks = pygame.time.get_ticks()
            
            if game_state == "PLAYING":
                elapsed = (current_ticks - start_ticks) / 1000.0
                time_left = max(0, duracao_segundos - int(elapsed))
                if time_left == 0: game_state = "WON"

            for event in pygame.event.get():
                if event.type == pygame.QUIT: return False 
                if event.type == pygame.KEYDOWN:
                    if game_state == "PLAYING":
                        if event.key == pygame.K_ESCAPE: return True
                        if event.key == pygame.K_LEFT and ship_x > 0: ship_x -= 1
                        if event.key == pygame.K_RIGHT and ship_x < COLS - 1: ship_x += 1
                        if event.key == pygame.K_UP and ship_z > 0: ship_z -= 1
                        if event.key == pygame.K_DOWN and ship_z < ROWS - 1: ship_z += 1
                    else:
                        if event.key == pygame.K_ESCAPE: return True
                        if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                            restarting = True

            if restarting: break

            if game_state == "PLAYING":
                if current_ticks - last_meteor_time > meteor_spawn_interval:
                    col_spawn = random.randint(0, COLS - 1)
                    meteoros.append({'x': col_spawn, 'z': ROWS, 'dx': 0, 'dz': -1})
                    
                    if nivel >= 2 and random.choice([True, False]): 
                        row_spawn = random.randint(0, ROWS - 1)
                        meteoros.append({'x': -1 if random.choice([True, False]) else COLS, 
                                         'z': row_spawn, 
                                         'dx': 1 if random.choice([True, False]) else -1, 
                                         'dz': 0})
                    last_meteor_time = current_ticks
                
                meteor_move_timer += dt
                if meteor_move_timer > meteor_move_interval:
                    meteor_move_timer = 0
                    for m in meteoros:
                        m['x'] += m['dx']
                        m['z'] += m['dz']
                    meteoros = [m for m in meteoros if -2 <= m['z'] <= ROWS + 1 and -2 <= m['x'] <= COLS + 1]
                    
                    for m in meteoros: # Colisao
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
            
            if game_state != "LOST" or (pygame.time.get_ticks() % 500 < 250):
                nx, ny, nz = get_world_pos(ship_x, ship_z)
                glPushMatrix()
                glTranslate(nx, ny, nz)
                # Animação suave de flutuação
                glTranslate(0, math.sin(tempo_fundo*0.1)*0.2, 0) 
                desenhar_nave_triangulo(tex_nave) 
                glPopMatrix()

            glEnable(GL_TEXTURE_2D) 
            for m in meteoros:
                mx, my, mz = get_world_pos(m['x'], m['z'])
                glPushMatrix()
                glTranslate(mx, my, mz)
                fundo.desenhar_esfera_texturizada(1.0, tex_meteoro)
                glPopMatrix()
            glDisable(GL_TEXTURE_2D) # Desativa ao terminar

            if game_state == "PLAYING":
                desenhar_texto_hud(f"Tempo: {time_left}s | Nivel: {nivel}", 10, display[1] - 40, display)
            else:
                cx, cy = display[0] // 2, display[1] // 2
                cor = (0, 255, 0, 255) if game_state == "WON" else (255, 0, 0, 255)
                msg = "VITORIA!" if game_state == "WON" else "GAME OVER"
                desenhar_texto_hud(msg, cx - 80, cy + 50, display, cor, 60)
                desenhar_texto_hud("[ENTER] Jogar Novamente", cx - 140, cy - 20, display)
                desenhar_texto_hud("[ESC] Voltar ao Menu", cx - 110, cy - 60, display, (200, 200, 200, 255), 24)

            pygame.display.flip()

def main():
    pygame.init()
    display = (1280, 720)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Space Dodge")

    fundo.init_opengl()
    fundo.init_all_textures() 

    while True:
        comando, tempo, nivel = menu.executar(display)
        if comando == "JOGAR":
            if not loop_jogo(display, tempo, nivel): break
        elif comando == "MAPA":
            if not visualizar_mapa(display): break
        elif comando is None:
            break
    pygame.quit()

if __name__ == "__main__":
    main()