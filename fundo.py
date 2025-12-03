import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import random
import struct

# Tenta importar PIL para carregar imagens reais. Se falhar, usaremos placeholders.
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("AVISO: Biblioteca Pillow (PIL) não encontrada. Usando texturas procedurais simples.")

# ================= CONFIGURAÇÕES =================
# Adicionamos a chave 'texture_file' e um placeholder para 'tex_id'
PLANETAS = [
    {"nome": "Mercurio", "raio": 0.4, "dist": 6,  "vel": 4.5, "cor_base": (0.7, 0.7, 0.7), "tex_file": "mercurio.jpg", "tex_id": None},
    {"nome": "Venus",    "raio": 0.6, "dist": 9,  "vel": 3.5, "cor_base": (1.0, 0.8, 0.2), "tex_file": "venus.png", "tex_id": None},
    {"nome": "Terra",    "raio": 0.6, "dist": 12, "vel": 2.5, "cor_base": (0.0, 0.0, 1.0), "tex_file": "terra.jpg", "tex_id": None},
    {"nome": "Marte",    "raio": 0.5, "dist": 15, "vel": 2.0, "cor_base": (1.0, 0.2, 0.0), "tex_file": "marte.jpg", "tex_id": None},
    {"nome": "Jupiter",  "raio": 1.4, "dist": 22, "vel": 1.2, "cor_base": (0.9, 0.6, 0.4), "tex_file": "jupiter.png", "tex_id": None},
    {"nome": "Saturno",  "raio": 1.2, "dist": 30, "vel": 0.9, "cor_base": (0.8, 0.7, 0.5), "tex_file": "saturno.png", "tex_id": None},
    {"nome": "Urano",    "raio": 0.9, "dist": 38, "vel": 0.6, "cor_base": (0.4, 0.9, 0.9), "tex_file": "urano.jpg", "tex_id": None},
    {"nome": "Netuno",   "raio": 0.9, "dist": 45, "vel": 0.4, "cor_base": (0.1, 0.1, 0.8), "tex_file": "netuno.png", "tex_id": None},
]

LUA_TERRA = {"raio": 0.2, "dist": 1.8, "vel": 10.0, "cor_base": (0.8, 0.8, 0.8), "tex_file": "lua.png", "tex_id": None}
SOL_CFG = {"raio": 3.5, "cor_base": (1.0, 0.8, 0.2), "tex_file": "sol.png", "tex_id": None}
ANEIS_SATURNO_CFG = {"tex_file": "saturno_aneis.png", "tex_id": None, "cor_base": (0.7, 0.6, 0.4)}

# =================GERENCIAMENTO DE TEXTURAS =================

def gerar_textura_procedural(cor_rgb, largura=64, altura=64):
    """Cria uma imagem falsa na memória com ruído baseado na cor fornecida."""
    data = bytearray()
    r_base, g_base, b_base = [int(c * 255) for c in cor_rgb]
    for _ in range(altura):
        for _ in range(largura):
            # Adiciona um pouco de ruído aleatório à cor base
            noise = random.randint(-30, 30)
            r = max(0, min(255, r_base + noise))
            g = max(0, min(255, g_base + noise))
            b = max(0, min(255, b_base + noise))
            data.extend([r, g, b, 255]) # RGBA
    return data, largura, altura

def load_texture(filename, cor_placeholder_rgb=None):
    """Carrega uma imagem e cria um ID de textura OpenGL."""
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)

    # Configurações de filtragem (importante para não ficar muito pixelado)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    # Configurações de "embrulho" da textura
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    
    img_data = None
    width, height = 0, 0
    loaded_real = False

    # --- TENTATIVA DE CARREGAR IMAGEM REAL (Requer Pillow e o arquivo) ---
    if PIL_AVAILABLE:
        try:
            img = Image.open(filename)
            img = img.convert("RGBA") # Garante formato consistente
            img_data = img.tobytes("raw", "RGBA", 0, -1)
            width, height = img.size
            loaded_real = True
            print(f"Textura carregada: {filename}")
        except IOError:
             print(f"Arquivo não encontrado: {filename}. Usando procedural.")

    # --- FALLBACK: GERAR TEXTURA PROCEDURAL SE FALHAR ---
    if not loaded_real and cor_placeholder_rgb:
         img_data, width, height = gerar_textura_procedural(cor_placeholder_rgb)
    
    if img_data:
        # Envia os dados da imagem para a GPU
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
    else:
        print(f"ERRO FATAL: Não foi possível gerar textura para {filename}")

    return texture_id

def init_all_textures():
    """Carrega todas as texturas necessárias antes do loop principal"""
    global SOL_CFG, LUA_TERRA, ANEIS_SATURNO_CFG
    
    # Habilita texturização 2D globalmente
    glEnable(GL_TEXTURE_2D)
    
    # O modo MODULATE multiplica a cor da textura pela cor do objeto/luz.
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)

    SOL_CFG["tex_id"] = load_texture(SOL_CFG["tex_file"], SOL_CFG["cor_base"])
    LUA_TERRA["tex_id"] = load_texture(LUA_TERRA["tex_file"], LUA_TERRA["cor_base"])
    ANEIS_SATURNO_CFG["tex_id"] = load_texture(ANEIS_SATURNO_CFG["tex_file"], ANEIS_SATURNO_CFG["cor_base"])

    for planeta in PLANETAS:
        planeta["tex_id"] = load_texture(planeta["tex_file"], planeta["cor_base"])


# ================= FUNÇÕES DE DESENHO ATUALIZADAS =================
def desenhar_esfera_texturizada(raio, texture_id):
    """Desenha uma esfera aplicando a textura informada."""
    # IMPORTANTE: Definir a cor para branco puro.
    # Se a cor for diferente (ex: vermelho), a textura será tingida de vermelho.
    glColor3f(1.0, 1.0, 1.0)

    # Vincula a textura que queremos usar agora
    glBindTexture(GL_TEXTURE_2D, texture_id)
    
    quadric = gluNewQuadric()
    gluQuadricDrawStyle(quadric, GLU_FILL) 
    gluQuadricNormals(quadric, GLU_SMOOTH)
    
    # --- A MÁGICA ACONTECE AQUI ---
    # Diz ao objeto quadric para gerar coordenadas de textura (UV mapping)
    gluQuadricTexture(quadric, GL_TRUE) 
    
    gluSphere(quadric, raio, 32, 32)
    gluDeleteQuadric(quadric)


def desenhar_anel_texturizado(raio_interno, raio_externo, texture_id):
    # Habilita blend para transparência (se a textura dos anéis for um PNG com fundo transparente)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    glColor4f(1.0, 1.0, 1.0, 0.8) # Um pouco de transparência global

    glBindTexture(GL_TEXTURE_2D, texture_id)
    quadric = gluNewQuadric()
    gluQuadricDrawStyle(quadric, GLU_FILL)
    gluQuadricNormals(quadric, GLU_FLAT)
    # Habilita textura para o disco
    gluQuadricTexture(quadric, GL_TRUE)
    
    gluDisk(quadric, raio_interno, raio_externo, 40, 1)
    gluDeleteQuadric(quadric)
    
    glDisable(GL_BLEND)

# ================= CONFIGURAÇÃO OPENGL BASE =================
def init_opengl():
    glClearColor(0.0, 0.0, 0.0, 1.0) 
    glEnable(GL_DEPTH_TEST)
    
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    # GL_COLOR_MATERIAL é menos necessário com texturas, mas mantemos por segurança
    glEnable(GL_COLOR_MATERIAL) 

    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.1, 0.1, 0.1, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.2, 1.2, 1.2, 1.0])
    glLightfv(GL_LIGHT0, GL_SPECULAR, [0.5, 0.5, 0.5, 1.0]) # Especular reduzido para texturas

    glShadeModel(GL_SMOOTH)

# ================= LOOP PRINCIPAL =================
def main():
    pygame.init()
    
    # --- ALTERAÇÃO AQUI: Resolução 1440p (Quad HD) ---
    largura = 2560
    altura = 1440
    display = (largura, altura)
    
    # Adicionei | pygame.FULLSCREEN para garantir que ocupe a tela toda corretamente
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL | pygame.FULLSCREEN)
    
    pygame.display.set_caption("Sistema Solar 1440p")

    glMatrixMode(GL_PROJECTION)
    # A razão de aspecto (largura/altura) se ajusta automaticamente aqui
    gluPerspective(45, (display[0]/display[1]), 0.1, 200.0)
    
    glMatrixMode(GL_MODELVIEW)
    gluLookAt(0, 60, 80, 0, 0, 0, 0, 1, 0)
    
    init_opengl()
    init_all_textures()
    
    tempo_animacao = 0
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); quit()
            
            # Atalho para fechar com ESC (útil em tela cheia)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); quit()
                if event.key == pygame.K_UP: glTranslate(0,0,2)
                if event.key == pygame.K_DOWN: glTranslate(0,0,-2)
        # Habilita texturas para o desenho
        glEnable(GL_TEXTURE_2D)

        # ================= 1. O SOL =================
        glPushMatrix()
        glLightfv(GL_LIGHT0, GL_POSITION, [0.0, 0.0, 0.0, 1.0])
        # Emissão alta para o sol brilhar muito e ignorar sombras
        glMaterialfv(GL_FRONT, GL_EMISSION, [0.9, 0.9, 0.9, 1.0])
        desenhar_esfera_texturizada(SOL_CFG["raio"], SOL_CFG["tex_id"]) 
        glMaterialfv(GL_FRONT, GL_EMISSION, [0.0, 0.0, 0.0, 1.0])
        glPopMatrix()

        # ================= 2. OS PLANETAS =================
        for planeta in PLANETAS:
            glPushMatrix() 
            angulo_planeta = (tempo_animacao * planeta["vel"]) % 360
            glRotate(angulo_planeta, 0, 1, 0)
            glTranslate(planeta["dist"], 0, 0)
            
            # Rotação do planeta sobre seu próprio eixo (para vermos a textura girando)
            glRotate(tempo_animacao * 2, 0, 1, 0) 

            desenhar_esfera_texturizada(planeta["raio"], planeta["tex_id"])

            # ================= 3. A LUA DA TERRA =================
            if planeta["nome"] == "Terra":
                glPushMatrix()
                angulo_lua = (tempo_animacao * LUA_TERRA["vel"]) % 360
                glRotate(angulo_lua, 0.1, 1, 0) 
                glTranslate(LUA_TERRA["dist"], 0, 0)
                # Rotação da lua
                glRotate(tempo_animacao * 5, 0, 1, 0)
                desenhar_esfera_texturizada(LUA_TERRA["raio"], LUA_TERRA["tex_id"])
                glPopMatrix()

            # ================= 4. ANÉIS DE SATURNO =================
            if planeta["nome"] == "Saturno":
                glPushMatrix()
                glRotate(45, 1, 0, 0) 
                # Anéis usam uma função de desenho diferente
                desenhar_anel_texturizado(planeta["raio"] + 0.3, planeta["raio"] + 1.5, ANEIS_SATURNO_CFG["tex_id"])
                glPopMatrix()
            
            glPopMatrix()

        glDisable(GL_TEXTURE_2D)
        tempo_animacao += 0.5
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()