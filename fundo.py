import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

# ================= CONFIGURAÇÕES =================
# As escalas (raio, distância) não são reais para permitir visualização em tela.
PLANETAS = [
    {"nome": "Mercurio", "raio": 0.4, "dist": 6,  "vel": 4.5, "cor": (0.7, 0.7, 0.7)},
    {"nome": "Venus",    "raio": 0.6, "dist": 9,  "vel": 3.5, "cor": (1.0, 0.8, 0.2)},
    {"nome": "Terra",    "raio": 0.6, "dist": 12, "vel": 2.5, "cor": (0.0, 0.0, 1.0)},
    {"nome": "Marte",    "raio": 0.5, "dist": 15, "vel": 2.0, "cor": (1.0, 0.2, 0.0)},
    {"nome": "Jupiter",  "raio": 1.4, "dist": 22, "vel": 1.2, "cor": (0.9, 0.6, 0.4)},
    {"nome": "Saturno",  "raio": 1.2, "dist": 30, "vel": 0.9, "cor": (0.8, 0.7, 0.5)},
    {"nome": "Urano",    "raio": 0.9, "dist": 38, "vel": 0.6, "cor": (0.4, 0.9, 0.9)},
    {"nome": "Netuno",   "raio": 0.9, "dist": 45, "vel": 0.4, "cor": (0.1, 0.1, 0.8)},
]

# Configuração da Lua
LUA_TERRA = {"raio": 0.2, "dist": 1.8, "vel": 10.0, "cor": (0.8, 0.8, 0.8)}

# ================= FUNÇÕES AUXILIARES =================
def desenhar_esfera(raio, cor):
    """Desenha uma esfera sólida com a cor especificada."""
    glColor3fv(cor)
    quadric = gluNewQuadric()
    # GLU_FILL garante que ela seja sólida e reaja à luz
    gluQuadricDrawStyle(quadric, GLU_FILL) 
    # Gerar normais é crucial para a iluminação funcionar na esfera
    gluQuadricNormals(quadric, GLU_SMOOTH) 
    gluSphere(quadric, raio, 32, 32)
    gluDeleteQuadric(quadric)

def desenhar_anel_saturno(raio_interno, raio_externo, cor):
    """Desenha um disco plano com um buraco no meio."""
    glColor3fv(cor)
    quadric = gluNewQuadric()
    gluQuadricDrawStyle(quadric, GLU_FILL)
    gluQuadricNormals(quadric, GLU_FLAT)
    # gluDisk desenha no plano XY (z=0)
    gluDisk(quadric, raio_interno, raio_externo, 40, 1)
    gluDeleteQuadric(quadric)

def init_opengl():
    """Configurações iniciais do estado do OpenGL"""
    glClearColor(0.0, 0.0, 0.0, 1.0) # Fundo preto
    glEnable(GL_DEPTH_TEST)          # Z-buffer (profundidade)
    
    # --- Configuração de Iluminação ---
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    
    # GL_COLOR_MATERIAL faz com que o comando glColor afete 
    # as propriedades difusas e ambientes do material do objeto.
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)

    # Parâmetros da luz 0 (Luz branca intensa)
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.1, 0.1, 0.1, 1.0]) # Luz ambiente fraca
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.2, 1.2, 1.2, 1.0]) # Luz direcional forte
    glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0]) # Brilho especular

    # Para os anéis e objetos planos ficarem melhores
    glShadeModel(GL_SMOOTH)

# ================= LOOP PRINCIPAL =================
def main():
    pygame.init()
    display = (1024, 768)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Sistema Solar: Terra+Lua e Saturno+Anéis")

    # Configuração da Câmera
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, (display[0]/display[1]), 0.1, 200.0)
    
    glMatrixMode(GL_MODELVIEW)
    # Posiciona a câmera: Olho(X,Y,Z), Centro(X,Y,Z), Vetor Cima(X,Y,Z)
    # Olhando um pouco mais de cima para ver os anéis melhor
    gluLookAt(0, 60, 80, 0, 0, 0, 0, 1, 0)
    
    init_opengl()
    
    tempo_animacao = 0
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            # Zoom simples com teclas para cima/baixo
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP: glTranslate(0,0,2)
                if event.key == pygame.K_DOWN: glTranslate(0,0,-2)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # ================= 1. O SOL (Emissor de Luz) =================
        glPushMatrix()
        # Define a posição da luz no centro (onde o sol será desenhado)
        # O 4º parâmetro '1.0' indica que é uma luz posicional (pontual), não direcional.
        glLightfv(GL_LIGHT0, GL_POSITION, [0.0, 0.0, 0.0, 1.0])
        
        # Faz o sol "brilhar" (emissão própria) para não ficar sombreado por ele mesmo
        glMaterialfv(GL_FRONT, GL_EMISSION, [1.0, 0.9, 0.2, 1.0])
        desenhar_esfera(3.5, (1.0, 0.8, 0.2)) 
        # Desliga a emissão para os próximos objetos
        glMaterialfv(GL_FRONT, GL_EMISSION, [0.0, 0.0, 0.0, 1.0])
        glPopMatrix()

        # ================= 2. OS PLANETAS =================
        for planeta in PLANETAS:
            glPushMatrix() # [PILHA: SOL] Salva o centro do universo
            
            # --- Órbita do Planeta ---
            angulo_planeta = (tempo_animacao * planeta["vel"]) % 360
            glRotate(angulo_planeta, 0, 1, 0) # Gira em torno do Sol (eixo Y)
            glTranslate(planeta["dist"], 0, 0) # Move para a distância orbital
            
            # --- Desenha o Planeta ---
            # Neste momento, a origem (0,0,0) local é o centro do planeta atual
            desenhar_esfera(planeta["raio"], planeta["cor"])

            # ================= 3. A LUA DA TERRA =================
            ### NOVO: Lógica da Lua ###
            if planeta["nome"] == "Terra":
                # Estamos no centro da Terra agora. Vamos criar uma nova "camada" na pilha.
                glPushMatrix() # [PILHA: SOL -> TERRA]
                
                # Órbita da Lua (mais rápida que o planeta)
                angulo_lua = (tempo_animacao * LUA_TERRA["vel"]) % 360
                
                # Gira em torno da Terra. Inclinei um pouco o eixo (1,1,0) para ficar mais interessante
                glRotate(angulo_lua, 0.1, 1, 0) 
                glTranslate(LUA_TERRA["dist"], 0, 0)
                
                desenhar_esfera(LUA_TERRA["raio"], LUA_TERRA["cor"])
                
                glPopMatrix() # [PILHA: SOL] Volta para o centro da Terra

            # ================= 4. ANÉIS DE SATURNO =================
            ### NOVO: Lógica dos Anéis ###
            if planeta["nome"] == "Saturno":
                # Estamos no centro de Saturno. Os anéis são estáticos em relação ao planeta.
                glPushMatrix() # [PILHA: SOL -> SATURNO] Salva a orientação de Saturno
                
                # Inclina os anéis. gluDisk desenha no plano Z=0.
                # Rotacionamos no eixo X para incliná-los em direção à câmera.
                glRotate(45, 1, 0, 0) 
                
                # Raio interno um pouco maior que o planeta, raio externo maior ainda
                desenhar_anel_saturno(planeta["raio"] + 0.3, planeta["raio"] + 1.5, (0.7, 0.6, 0.4))
                
                glPopMatrix() # [PILHA: SOL] Restaura a orientação
            
            glPopMatrix() # [PILHA: VAZIA] Volta para o centro do Sol para o próximo planeta

        # Atualiza tempo
        tempo_animacao += 0.5
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()