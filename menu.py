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

def executar(display):
    """
    Retorna:
    "JOGAR" -> Inicia o jogo
    "MAPA"  -> Visualiza o mapa
    None    -> Sai do jogo
    """
    clock = pygame.time.Clock()
    tempo_fundo = 0
    largura, altura = display
    cx = largura // 2

    # Opções do Menu
    opcoes = ["JOGAR", "VISUALIZAR MAPA", "SAIR"]
    selecionado = 0 # Índice da opção atual

    while True:
        clock.tick(60)
        tempo_fundo += 0.2

        # --- INPUT ---
        for event in pygame.event.get():
            if event.type == QUIT:
                return None
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return None
                
                # Navegação
                if event.key == K_UP:
                    selecionado = (selecionado - 1) % len(opcoes)
                if event.key == K_DOWN:
                    selecionado = (selecionado + 1) % len(opcoes)
                
                # Seleção
                if event.key == K_RETURN or event.key == K_KP_ENTER:
                    if selecionado == 0: return "JOGAR"
                    if selecionado == 1: return "MAPA"
                    if selecionado == 2: return None

        # --- DESENHO ---
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # 1. Fundo
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, (display[0]/display[1]), 0.1, 200.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(0, 30, 60, 0, 0, 0, 0, 1, 0)
        
        fundo.desenhar_cenario(tempo_fundo)

        # 2. Título
        desenhar_texto("SPACE DODGE", cx - 180, altura - 150, display, 70, (255, 200, 50, 255))
        
        # 3. Opções
        y_start = altura // 2
        for i, op in enumerate(opcoes):
            # Se for a opção selecionada, pinta de Verde, senão Branco
            if i == selecionado:
                cor = (0, 255, 0, 255)
                prefixo = "> "
            else:
                cor = (200, 200, 200, 255)
                prefixo = "  "
            
            desenhar_texto(prefixo + op, cx - 100, y_start - (i * 50), display, 40, cor)

        # Instruções
        desenhar_texto("Use SETAS e ENTER", cx - 100, 50, display, 24, (150, 150, 150, 255))

        pygame.display.flip()