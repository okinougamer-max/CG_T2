import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import random
import math
import fundo
import menu

COLS, ROWS = 8, 8
CELL_SIZE = 4.0 
GRID_Y = 5.0 

def get_world_pos(gx, gz):
    wx = (gx - (COLS-1)/2.0) * CELL_SIZE
    wz = (gz - (ROWS-1)/2.0) * CELL_SIZE 
    return wx, GRID_Y, wz

def desenhar_nave_triangulo(texture_id=None):
    glEnable(GL_TEXTURE_2D) if texture_id else glDisable(GL_TEXTURE_2D)
    if texture_id: glBindTexture(GL_TEXTURE_2D, texture_id)
    glColor3f(1, 1, 1)
    
    glBegin(GL_TRIANGLES)
    glNormal3f(0, 1, 0)
    glTexCoord2f(0.5, 1.0); glVertex3f(0.0, 0.0, -1.5)
    glTexCoord2f(0.0, 0.0); glVertex3f(-1.0, 0.0, 1.5)
    glTexCoord2f(1.0, 0.0); glVertex3f(1.0, 0.0, 1.5)
    glEnd()
    glDisable(GL_TEXTURE_2D)

def visualizar_mapa(display):
    clock = pygame.time.Clock()
    cam_x, cam_y, cam_z = 0, 30, 60
    tempo = 0
    while True:
        clock.tick(60)
        tempo += 0.5
        for event in pygame.event.get():
            if event.type == QUIT: return False 
            if event.type == KEYDOWN and event.key == K_ESCAPE: return True 

        keys = pygame.key.get_pressed()
        if keys[K_LEFT]: cam_x -= 1
        if keys[K_RIGHT]: cam_x += 1
        if keys[K_UP]: cam_z -= 1
        if keys[K_DOWN]: cam_z += 1
        if keys[K_w]: cam_y -= 1 
        if keys[K_s]: cam_y += 1 

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity(); gluPerspective(45, (display[0]/display[1]), 0.1, 400.0)
        glMatrixMode(GL_MODELVIEW); glLoadIdentity()
        gluLookAt(cam_x, cam_y, cam_z, cam_x, 0, cam_z - 40, 0, 1, 0)

        fundo.desenhar_cenario(tempo)
        
        # Grade simples
        glDisable(GL_TEXTURE_2D); glColor3f(0, 1, 0)
        glBegin(GL_LINES)
        sz = ROWS * CELL_SIZE
        sx = COLS * CELL_SIZE
        start_x, start_z = -sx/2, -sz/2
        for i in range(COLS + 1):
            glVertex3f(start_x + i*CELL_SIZE, GRID_Y, start_z)
            glVertex3f(start_x + i*CELL_SIZE, GRID_Y, start_z + sz)
        for i in range(ROWS + 1):
            glVertex3f(start_x, GRID_Y, start_z + i*CELL_SIZE)
            glVertex3f(start_x + sx, GRID_Y, start_z + i*CELL_SIZE)
        glEnd()

        menu.desenhar_texto("MODO OBSERVADOR", 10, display[1]-40, display, 32, (0,255,255,255))
        pygame.display.flip()

def loop_jogo(display, duracao, nivel):
    ship_x, ship_z = 4, 0
    meteoros = []
    state = "jogando"
    start_t = pygame.time.get_ticks()
    last_spawn = 0
    move_timer = 0
    tempo_fundo = 0
    clock = pygame.time.Clock()

    tex_meteoro = fundo.METEORO_CFG["id"]
    tex_nave = fundo.NAVE_CFG["id"]

    while True:
        dt = clock.tick(60)
        tempo_fundo += 0.5
        now = pygame.time.get_ticks()
        
        if state == "jogando":
            time_left = max(0, duracao - int((now - start_t) / 1000.0))
            if time_left == 0: state = "WON"

        for event in pygame.event.get():
            if event.type == QUIT: return False
            if event.type == KEYDOWN:
                if state == "jogando":
                    # Durante o jogo, ESC volta ao menu
                    if event.key == K_ESCAPE: return "MENU"
                    if event.key == K_LEFT and ship_x > 0: ship_x -= 1
                    if event.key == K_RIGHT and ship_x < COLS-1: ship_x += 1
                    if event.key == K_UP and ship_z > 0: ship_z -= 1
                    if event.key == K_DOWN and ship_z < ROWS-1: ship_z += 1
                else:
                    # Fim de jogo: ESC -> Menu, ENTER -> Reiniciar
                    if event.key == K_ESCAPE: return "MENU"
                    if event.key in (K_RETURN, K_KP_ENTER): return "RESTART"

        if state == "jogando":
            if now - last_spawn > (800 if nivel < 3 else 400):
                meteoros.append({'x': random.randint(0, COLS-1), 'z': ROWS, 'dx':0, 'dz':-1})
                if nivel >= 2 and random.choice([True, False]):
                    meteoros.append({'x': -1 if random.choice([0,1]) else COLS, 'z': random.randint(0, ROWS-1), 'dx': 1 if random.choice([0,1]) else -1, 'dz': 0})
                last_spawn = now
            
            move_timer += dt
            if move_timer > 200:
                move_timer = 0
                for m in meteoros:
                    m['x'] += m['dx']; m['z'] += m['dz']
                    if m['x'] == ship_x and m['z'] == ship_z: state = "LOST"
                meteoros = [m for m in meteoros if -2 <= m['z'] <= ROWS+1 and -2 <= m['x'] <= COLS+1]

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity(); gluPerspective(45, (display[0]/display[1]), 0.1, 200.0)
        glMatrixMode(GL_MODELVIEW); glLoadIdentity()
        gluLookAt(0, 30, 50, 0, 0, 0, 0, 1, 0)

        fundo.desenhar_cenario(tempo_fundo)
        
        # Grade
        glDisable(GL_TEXTURE_2D); glColor3f(0, 1, 0)
        glBegin(GL_LINES)
        sz, sx = ROWS * CELL_SIZE, COLS * CELL_SIZE
        st_x, st_z = -sx/2, -sz/2
        for i in range(COLS+1): glVertex3f(st_x+i*CELL_SIZE, GRID_Y, st_z); glVertex3f(st_x+i*CELL_SIZE, GRID_Y, st_z+sz)
        for i in range(ROWS+1): glVertex3f(st_x, GRID_Y, st_z+i*CELL_SIZE); glVertex3f(st_x+sx, GRID_Y, st_z+i*CELL_SIZE)
        glEnd()

        if state != "LOST" or (now % 500 < 250):
            nx, ny, nz = get_world_pos(ship_x, ship_z)
            glPushMatrix()
            glTranslate(nx, ny + math.sin(tempo_fundo*0.1)*0.2, nz)
            desenhar_nave_triangulo(tex_nave)
            glPopMatrix()

        glEnable(GL_TEXTURE_2D) 
        for m in meteoros:
            mx, my, mz = get_world_pos(m['x'], m['z'])
            glPushMatrix()
            glTranslate(mx, my, mz)
            fundo.desenhar_esfera(1.0, tex_meteoro)
            glPopMatrix()
        glDisable(GL_TEXTURE_2D)

        if state == "jogando":
            menu.desenhar_texto(f"Tempo: {time_left}s | Nivel: {nivel}", 10, display[1]-40, display)
        else:
            # HUD de Fim de Jogo
            cx, cy = display[0]//2, display[1]//2
            msg = "VITORIA!" if state == "WON" else "GAME OVER"
            c = (0, 255, 0, 255) if state == "WON" else (255, 0, 0, 255)
            menu.desenhar_texto(msg, cx-80, cy+50, display, 60, c)
            menu.desenhar_texto("[ENTER] Jogar Novamente", cx-140, cy-20, display)
            menu.desenhar_texto("[ESC] Voltar ao Menu", cx-110, cy-60, display, 24, (200, 200, 200, 255))

        pygame.display.flip()

def main():
    pygame.init()
    display = (1280, 720)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Space Dodge")

    fundo.init_opengl()
    fundo.init_all_textures() 

    while True:
        res = menu.executar(display)
        if not res or res[0] is None: break
        cmd, tempo, nivel = res
        
        if cmd == "JOGAR":
            while True: 
                status = loop_jogo(display, tempo, nivel)
                
                if status == "MENU": 
                    break 
                elif status == False: 
                    pygame.quit() 
                    return
                
        elif cmd == "MAPA":
            if not visualizar_mapa(display): break 
            
    pygame.quit()

if __name__ == "__main__":
    main()