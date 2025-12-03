import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math

# Configurações de Tela
DISPLAY_WIDTH = 1200
DISPLAY_HEIGHT = 800

# Estrutura para armazenar IDs de texturas
textures = {}

def load_texture(filename, texture_name):
    """ Carrega uma imagem e a transforma em textura OpenGL """
    try:
        texture_surface = pygame.image.load(filename)
        texture_data = pygame.image.tostring(texture_surface, "RGB", 1)
        width = texture_surface.get_width()
        height = texture_surface.get_height()

        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        
        # Parâmetros da textura
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, texture_data)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        
        textures[texture_name] = tex_id
        print(f"Textura '{filename}' carregada com sucesso.")
    except Exception as e:
        print(f"Erro ao carregar textura {filename}: {e}")
        textures[texture_name] = None

def init_gl():
    """ Configuração inicial do OpenGL """
    glEnable(GL_DEPTH_TEST) # Habilita profundidade (Z-buffer)
    glEnable(GL_TEXTURE_2D) # Habilita texturas
    
    # Configuração de Luz
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    
    # Luz ambiente fraca e difusa forte
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
    
    # Cor do material
    glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)
    
    gluPerspective(45, (DISPLAY_WIDTH / DISPLAY_HEIGHT), 0.1, 100.0)
    
    # Posição da Câmera (olhando de cima e inclinado)
    gluLookAt(0, 30, 40, 0, 0, 0, 0, 1, 0)

def draw_sphere(radius, texture_name):
    """ Desenha uma esfera com textura """
    quadric = gluNewQuadric()
    
    if textures.get(texture_name):
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, textures[texture_name])
        gluQuadricTexture(quadric, GL_TRUE)
        glColor3f(1, 1, 1) # Reset cor para branco para não tingir a textura
    else:
        glDisable(GL_TEXTURE_2D)
        # Cores de fallback caso não haja textura
        if texture_name == 'sol': glColor3f(1, 1, 0)
        elif texture_name == 'terra': glColor3f(0, 0, 1)
        else: glColor3f(0.5, 0.5, 0.5)

    gluSphere(quadric, radius, 32, 32)
    gluDeleteQuadric(quadric)

def draw_ring(inner, outer, texture_name):
    """ Desenha um disco (para os anéis de Saturno) """
    quadric = gluNewQuadric()
    
    if textures.get(texture_name):
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, textures[texture_name])
        gluQuadricTexture(quadric, GL_TRUE)
    else:
        glDisable(GL_TEXTURE_2D)
        glColor3f(0.8, 0.8, 0.6)

    # Rotaciona para o anel ficar plano
    glPushMatrix()
    glRotatef(90, 1, 0, 0) 
    gluDisk(quadric, inner, outer, 32, 1)
    glPopMatrix()
    gluDeleteQuadric(quadric)

def main():
    pygame.init()
    pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Sistema Solar PyOpenGL")
    
    init_gl()
    
    # Carregar Texturas (Substitua pelos nomes reais dos seus arquivos)
    load_texture("sol.jpg", "sol")
    load_texture("mercurio.jpg", "mercurio")
    load_texture("venus.jpg", "venus")
    load_texture("terra.jpg", "terra")
    load_texture("lua.jpg", "lua")
    load_texture("marte.jpg", "marte")
    load_texture("jupiter.jpg", "jupiter")
    load_texture("saturno.jpg", "saturno")
    load_texture("anelSaturno.png", "aneis") # Textura para anéis
    load_texture("urano.jpg", "urano")
    load_texture("netuno.jpg", "netuno")

    # Configuração dos Planetas: (Nome, Distancia, Raio, VelocidadeOrbita, Textura)
    # Nota: Escalas não são reais para permitir visualização
    planets_data = [
        ("mercurio", 4.0, 0.3, 1.5, "mercurio"),
        ("venus", 6.0, 0.5, 1.2, "venus"),
        ("terra", 9.0, 0.5, 1.0, "terra"), # Índice 2 é a Terra (usado para Lua)
        ("marte", 12.0, 0.4, 0.8, "marte"),
        ("jupiter", 18.0, 1.2, 0.4, "jupiter"),
        ("saturno", 24.0, 1.0, 0.3, "saturno"), # Índice 5 é Saturno
        ("urano", 30.0, 0.8, 0.2, "urano"),
        ("netuno", 36.0, 0.8, 0.1, "netuno")
    ]

    t = 0 # Tempo para animação

    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # Reposiciona câmera a cada frame (caso queira adicionar movimento depois)
        gluLookAt(0, 40, 50, 0, 0, 0, 0, 1, 0)

        # 1. DESENHAR O SOL (Fonte de Luz)
        # Desabilitamos a iluminação para desenhar o Sol, para que ele pareça
        # "brilhar" por conta própria, ignorando sombras.
        glDisable(GL_LIGHTING)
        glPushMatrix()
        draw_sphere(2.5, "sol") # Sol um pouco maior
        glPopMatrix()
        
        # Posiciona a luz OpenGL no centro (onde está o Sol)
        # O 4º parâmetro 1.0 indica que é uma luz pontual (Positional Light)
        glEnable(GL_LIGHTING)
        glLightfv(GL_LIGHT0, GL_POSITION, [0.0, 0.0, 0.0, 1.0])

        # 2. DESENHAR PLANETAS
        for i, p_data in enumerate(planets_data):
            name, dist, radius, speed, tex = p_data
            
            angle = t * speed
            
            glPushMatrix()
            
            # Translação orbital (Girar o "universo" para posicionar o planeta)
            glRotatef(angle, 0, 1, 0)
            glTranslatef(dist, 0, 0)
            
            # Rotação do próprio planeta (spin)
            glPushMatrix() # Salva a posição antes do spin
            glRotatef(t * 20, 0, 1, 0)
            draw_sphere(radius, tex)
            glPopMatrix() # Volta para o centro do planeta (sem spin) para desenhar filhos

            # --- CASOS ESPECIAIS ---
            
            # A) LUA (Orbitando a Terra)
            if name == "terra":
                # Já estamos na posição da Terra. Vamos nos mover relativo a ela.
                glRotatef(t * 3, 0, 1, 0) # Orbita da lua
                glTranslatef(1.2, 0, 0)   # Distancia Lua-Terra
                draw_sphere(0.15, "lua")
            
            # B) ANÉIS DE SATURNO
            if name == "saturno":
                # Anéis
                glPushMatrix()
                glRotatef(45, 1, 0, 0) # Inclinação dos anéis
                draw_ring(1.2, 2.0, "aneis")
                glPopMatrix()

            glPopMatrix() # Volta para o centro do Sistema Solar (0,0,0)

        t += 0.5 # Incrementa tempo
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()