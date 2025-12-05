import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import fundo

def desenhar_texto(texto, x, y, display, tamanho=32, cor=(255, 255, 255, 255)):
    try:
        font = pygame.font.SysFont('arial', tamanho, bold=True)
    except:
        font = pygame.font.Font(None, tamanho)
        
    surface = font.render(texto, True, cor).convert_alpha()
    data = pygame.image.tostring(surface, "RGBA", True)
    w, h = surface.get_size()

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
    glDrawPixels(w, h, GL_RGBA, GL_UNSIGNED_BYTE, data)
    glDisable(GL_BLEND)
    glEnable(GL_DEPTH_TEST)
    
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()

def executar(display):
    clock = pygame.time.Clock()
    tempo_fundo, cx, cy = 0, display[0] // 2, display[1] // 2
    tempo_jogo, nivel_jogo = 15, 1
    opcoes = ["JOGAR", "TEMPO", "NIVEL", "VISUALIZAR MAPA", "SAIR"]
    selecionado = 0

    while True:
        clock.tick(60)
        tempo_fundo += 0.2

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                return None, 0, 1
            
            if event.type == KEYDOWN:
                if event.key == K_UP:   selecionado = (selecionado - 1) % 5
                if event.key == K_DOWN: selecionado = (selecionado + 1) % 5
                
                # Ajustes Laterais
                delta = -1 if event.key == K_LEFT else (1 if event.key == K_RIGHT else 0)
                if delta != 0:
                    if selecionado == 1: tempo_jogo = max(5, tempo_jogo + delta)
                    if selecionado == 2: nivel_jogo = max(1, min(3, nivel_jogo + delta))

                if event.key in (K_RETURN, K_KP_ENTER):
                    if selecionado == 0: return "JOGAR", tempo_jogo, nivel_jogo
                    if selecionado == 3: return "MAPA", 0, 1
                    if selecionado == 4: return None, 0, 1

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_PROJECTION); glLoadIdentity()
        gluPerspective(45, (display[0]/display[1]), 0.1, 200.0)
        glMatrixMode(GL_MODELVIEW); glLoadIdentity()
        gluLookAt(0, 30, 60, 0, 0, 0, 0, 1, 0)
        
        fundo.desenhar_cenario(tempo_fundo)
        desenhar_texto("SPACE DODGE", cx - 180, display[1] - 150, display, 70, (255, 200, 50, 255))
        
        textos = [
            "JOGAR", f"< TEMPO: {tempo_jogo}s >", f"< NIVEL: {nivel_jogo} >",
            "VISUALIZAR MAPA", "SAIR"
        ]

        for i, txt in enumerate(textos):
            cor = (0, 255, 0, 255) if i == selecionado else (200, 200, 200, 255)
            prefixo = "> " if i == selecionado else "  "
            desenhar_texto(prefixo + txt, cx - 100, cy - (i * 50), display, 40, cor)

        desc = ["", "Meteoros Verticais", "Verticais + Horizontais", "Velocidade Maxima!"][nivel_jogo]
        desenhar_texto(f"Nivel {nivel_jogo}: {desc}", cx - 150, 80, display, 20, (100, 255, 255, 255))
        pygame.display.flip()