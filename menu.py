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
    Retorna uma tupla: (COMANDO, TEMPO, NIVEL)
    """
    clock = pygame.time.Clock()
    tempo_fundo = 0
    largura, altura = display
    cx = largura // 2

    # Estado do Menu
    tempo_jogo = 30  # Tempo padrão
    nivel_jogo = 1   # Nível padrão
    
    # Índices das opções
    OP_JOGAR = 0
    OP_TEMPO = 1
    OP_NIVEL = 2
    OP_MAPA = 3
    OP_SAIR = 4
    
    selecionado = OP_JOGAR

    while True:
        clock.tick(60)
        tempo_fundo += 0.2

        # --- INPUT ---
        for event in pygame.event.get():
            if event.type == QUIT:
                return None, 0, 1
            
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return None, 0, 1
                
                # Navegação Cima/Baixo
                if event.key == K_UP:
                    selecionado = (selecionado - 1) % 5
                if event.key == K_DOWN:
                    selecionado = (selecionado + 1) % 5
                
                # Ajuste de Tempo
                if selecionado == OP_TEMPO:
                    if event.key == K_LEFT:
                        tempo_jogo = max(5, tempo_jogo - 1)
                    if event.key == K_RIGHT:
                        tempo_jogo += 1
                
                # Ajuste de Nível (1 a 3)
                if selecionado == OP_NIVEL:
                    if event.key == K_LEFT:
                        nivel_jogo = max(1, nivel_jogo - 1)
                    if event.key == K_RIGHT:
                        nivel_jogo = min(3, nivel_jogo + 1)

                # Seleção (Enter)
                if event.key == K_RETURN or event.key == K_KP_ENTER:
                    if selecionado == OP_JOGAR:
                        return "JOGAR", tempo_jogo, nivel_jogo
                    if selecionado == OP_TEMPO or selecionado == OP_NIVEL:
                        selecionado = OP_JOGAR 
                    if selecionado == OP_MAPA:
                        return "MAPA", 0, 1
                    if selecionado == OP_SAIR:
                        return None, 0, 1

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
        opcoes_lista = [
            "JOGAR",
            f"< TEMPO: {tempo_jogo}s >",
            f"< NIVEL: {nivel_jogo} >",
            "VISUALIZAR MAPA",
            "SAIR"
        ]

        y_start = altura // 2
        for i, texto in enumerate(opcoes_lista):
            if i == selecionado:
                cor = (0, 255, 0, 255)
                prefixo = "> "
            else:
                cor = (200, 200, 200, 255)
                prefixo = "  "
            
            offset_x = 100
            if i == OP_TEMPO or i == OP_NIVEL: offset_x = 120 

            desenhar_texto(prefixo + texto, cx - offset_x, y_start - (i * 50), display, 40, cor)

        # Instruções
        desenhar_texto("Use SETAS para ajustar Tempo e Nivel", cx - 180, 50, display, 24, (150, 150, 150, 255))
        
        # Descrição do nível atual (Feedback visual)
        desc_nivel = ""
        if nivel_jogo == 1: desc_nivel = "Nivel 1: Meteoros Verticais"
        elif nivel_jogo == 2: desc_nivel = "Nivel 2: Verticais + Horizontais"
        elif nivel_jogo == 3: desc_nivel = "Nivel 3: Velocidade Maxima!"
        
        desenhar_texto(desc_nivel, cx - 150, 80, display, 20, (100, 255, 255, 255))

        pygame.display.flip()