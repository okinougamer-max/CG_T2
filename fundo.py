import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import random
import os

# Tenta importar PIL para carregar imagens reais.
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("AVISO: Biblioteca Pillow (PIL) não encontrada. As texturas não serão carregadas.")
    print("Para corrigir, instale: pip install Pillow")

# ================= FUNÇÃO AUXILIAR PARA ENCONTRAR ARQUIVOS =================
def encontrar_arquivo(nome_arquivo):
    """
    Tenta encontrar o arquivo no diretório atual ou na pasta 'assets'.
    Retorna o caminho completo se encontrado, ou None se não existir.
    """
    # 1. Tenta no diretório atual
    if os.path.exists(nome_arquivo):
        return nome_arquivo
    
    # 2. Tenta na pasta assets/
    caminho_assets = os.path.join("assets", nome_arquivo)
    if os.path.exists(caminho_assets):
        return caminho_assets
        
    # 3. Tenta corrigir nomes comuns ou extensões trocadas (fallback)
    # Ex: urano.jpg não existe na raiz, mas urano.png existe
    nome_sem_ext, ext = os.path.splitext(nome_arquivo)
    alternativas = [
        nome_sem_ext + ".png",
        nome_sem_ext + ".jpg",
        os.path.join("assets", nome_sem_ext + ".png"),
        os.path.join("assets", nome_sem_ext + ".jpg")
    ]
    
    for alt in alternativas:
        if os.path.exists(alt):
            print(f"Aviso: '{nome_arquivo}' não encontrado, usando '{alt}' no lugar.")
            return alt

    return None

# ================= CONFIGURAÇÕES =================
# Atualizei os nomes para bater com os arquivos que você enviou
PLANETAS = [
    {"nome": "Mercurio", "raio": 0.4, "dist": 6,  "vel": 4.5, "cor_base": (0.7, 0.7, 0.7), "tex_file": "mercurio.jpg", "tex_id": None},
    {"nome": "Venus",    "raio": 0.6, "dist": 9,  "vel": 3.5, "cor_base": (1.0, 0.8, 0.2), "tex_file": "venus.png", "tex_id": None},
    {"nome": "Terra",    "raio": 0.6, "dist": 12, "vel": 2.5, "cor_base": (0.0, 0.0, 1.0), "tex_file": "terra.jpg", "tex_id": None},
    {"nome": "Marte",    "raio": 0.5, "dist": 15, "vel": 2.0, "cor_base": (1.0, 0.2, 0.0), "tex_file": "marte.jpg", "tex_id": None},
    {"nome": "Jupiter",  "raio": 1.4, "dist": 22, "vel": 1.2, "cor_base": (0.9, 0.6, 0.4), "tex_file": "jupiter.png", "tex_id": None},
    {"nome": "Saturno",  "raio": 1.2, "dist": 30, "vel": 0.9, "cor_base": (0.8, 0.7, 0.5), "tex_file": "saturno.png", "tex_id": None},
    # Nota: O arquivo enviado parece ser urano.png ou assets/urano.jpg. O buscador resolverá.
    {"nome": "Urano",    "raio": 0.9, "dist": 38, "vel": 0.6, "cor_base": (0.4, 0.9, 0.9), "tex_file": "urano.png", "tex_id": None},
    {"nome": "Netuno",   "raio": 0.9, "dist": 45, "vel": 0.4, "cor_base": (0.1, 0.1, 0.8), "tex_file": "netuno.png", "tex_id": None},
]

LUA_TERRA = {"raio": 0.2, "dist": 1.8, "vel": 10.0, "cor_base": (0.8, 0.8, 0.8), "tex_file": "lua.png", "tex_id": None}
SOL_CFG = {"raio": 3.5, "cor_base": (1.0, 0.8, 0.2), "tex_file": "sol.png", "tex_id": None}

# CORREÇÃO CRÍTICA: O nome do arquivo no seu upload é anelSaturno.png
ANEIS_SATURNO_CFG = {"tex_file": "anelSaturno.png", "tex_id": None, "cor_base": (0.7, 0.6, 0.4)}

# ================= GERENCIAMENTO DE TEXTURAS =================

def gerar_textura_procedural(cor_rgb, largura=64, altura=64):
    """Cria uma imagem falsa na memória com ruído baseado na cor fornecida."""
    data = bytearray()
    r_base, g_base, b_base = [int(c * 255) for c in cor_rgb]
    for _ in range(altura):
        for _ in range(largura):
            noise = random.randint(-30, 30)
            r = max(0, min(255, r_base + noise))
            g = max(0, min(255, g_base + noise))
            b = max(0, min(255, b_base + noise))
            data.extend([r, g, b, 255]) 
    return data, largura, altura

def load_texture(filename, cor_placeholder_rgb=None):
    """Carrega uma imagem e cria um ID de textura OpenGL."""
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)

    # Configurações de filtragem
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    
    img_data = None
    width, height = 0, 0
    loaded_real = False
    
    # Busca o caminho correto do arquivo
    caminho_real = encontrar_arquivo(filename)

    if PIL_AVAILABLE and caminho_real:
        try:
            img = Image.open(caminho_real)
            img = img.convert("RGBA")
            img_data = img.tobytes("raw", "RGBA", 0, -1)
            width, height = img.size
            loaded_real = True
            print(f"Textura carregada com sucesso: {caminho_real}")
        except IOError as e:
             print(f"Erro ao abrir imagem {caminho_real}: {e}")
    else:
        if not caminho_real:
            print(f"ARQUIVO NÃO ENCONTRADO: {filename} (Verifique se está na pasta assets)")
        elif not PIL_AVAILABLE:
            print(f"Pillow não instalado. Não foi possível carregar {filename}")

    # Fallback para cor sólida se falhar
    if not loaded_real and cor_placeholder_rgb:
         img_data, width, height = gerar_textura_procedural(cor_placeholder_rgb)
    
    if img_data:
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
    else:
        print(f"ERRO FATAL: Não foi possível gerar textura para {filename}")

    return texture_id

def init_all_textures():
    global SOL_CFG, LUA_TERRA, ANEIS_SATURNO_CFG
    
    glEnable(GL_TEXTURE_2D)
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)

    print("--- Carregando Texturas ---")
    SOL_CFG["tex_id"] = load_texture(SOL_CFG["tex_file"], SOL_CFG["cor_base"])
    LUA_TERRA["tex_id"] = load_texture(LUA_TERRA["tex_file"], LUA_TERRA["cor_base"])
    ANEIS_SATURNO_CFG["tex_id"] = load_texture(ANEIS_SATURNO_CFG["tex_file"], ANEIS_SATURNO_CFG["cor_base"])

    for planeta in PLANETAS:
        planeta["tex_id"] = load_texture(planeta["tex_file"], planeta["cor_base"])
    print("-------------------------")


# ================= FUNÇÕES DE DESENHO =================
def desenhar_esfera_texturizada(raio, texture_id):
    # Cor branca para garantir que a textura apareça com suas cores originais
    glColor3f(1.0, 1.0, 1.0)

    glBindTexture(GL_TEXTURE_2D, texture_id)
    
    quadric = gluNewQuadric()
    gluQuadricDrawStyle(quadric, GLU_FILL) 
    gluQuadricNormals(quadric, GLU_SMOOTH)
    gluQuadricTexture(quadric, GL_TRUE) 
    
    gluSphere(quadric, raio, 32, 32)
    gluDeleteQuadric(quadric)


def desenhar_anel_texturizado(raio_interno, raio_externo, texture_id):
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # Cor branca com leve transparência
    glColor4f(1.0, 1.0, 1.0, 0.9) 

    glBindTexture(GL_TEXTURE_2D, texture_id)
    quadric = gluNewQuadric()
    gluQuadricDrawStyle(quadric, GLU_FILL)
    gluQuadricNormals(quadric, GLU_FLAT)
    gluQuadricTexture(quadric, GL_TRUE)
    
    gluDisk(quadric, raio_interno, raio_externo, 40, 1)
    gluDeleteQuadric(quadric)
    
    glDisable(GL_BLEND)

# ================= CONFIGURAÇÃO OPENGL =================
def init_opengl():
    glClearColor(0.0, 0.0, 0.0, 1.0) 
    glEnable(GL_DEPTH_TEST)
    
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL) 

    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
    glLightfv(GL_LIGHT0, GL_SPECULAR, [0.5, 0.5, 0.5, 1.0])

    glShadeModel(GL_SMOOTH)

# ================= LOOP PRINCIPAL =================
def main():
    pygame.init()
    
    largura = 1280
    altura = 720
    display = (largura, altura)
    
    # Removido FULLSCREEN para facilitar testes e debug, adicione se quiser
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Sistema Solar Texturizado")

    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, (display[0]/display[1]), 0.1, 200.0)
    
    glMatrixMode(GL_MODELVIEW)
    gluLookAt(0, 40, 60, 0, 0, 0, 0, 1, 0)
    
    init_opengl()
    init_all_textures()
    
    tempo_animacao = 0
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); quit()
                if event.key == pygame.K_UP: glTranslate(0,0,2)
                if event.key == pygame.K_DOWN: glTranslate(0,0,-2)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        glEnable(GL_TEXTURE_2D)

        # 1. SOL
        glPushMatrix()
        glLightfv(GL_LIGHT0, GL_POSITION, [0.0, 0.0, 0.0, 1.0])
        glMaterialfv(GL_FRONT, GL_EMISSION, [1.0, 1.0, 1.0, 1.0]) # Sol brilha forte
        desenhar_esfera_texturizada(SOL_CFG["raio"], SOL_CFG["tex_id"]) 
        glMaterialfv(GL_FRONT, GL_EMISSION, [0.0, 0.0, 0.0, 1.0])
        glPopMatrix()

        # 2. PLANETAS
        for planeta in PLANETAS:
            glPushMatrix() 
            angulo_planeta = (tempo_animacao * planeta["vel"]) % 360
            glRotate(angulo_planeta, 0, 1, 0)
            glTranslate(planeta["dist"], 0, 0)
            
            glPushMatrix() # Salva estado antes da rotação do eixo
            glRotate(tempo_animacao * 2, 0, 1, 0) 
            desenhar_esfera_texturizada(planeta["raio"], planeta["tex_id"])
            glPopMatrix()

            # 3. LUA DA TERRA
            if planeta["nome"] == "Terra":
                glPushMatrix()
                angulo_lua = (tempo_animacao * LUA_TERRA["vel"]) % 360
                glRotate(angulo_lua, 0.1, 1, 0) 
                glTranslate(LUA_TERRA["dist"], 0, 0)
                desenhar_esfera_texturizada(LUA_TERRA["raio"], LUA_TERRA["tex_id"])
                glPopMatrix()

            # 4. ANÉIS DE SATURNO
            if planeta["nome"] == "Saturno":
                glPushMatrix()
                glRotate(45, 1, 0, 0) 
                desenhar_anel_texturizado(planeta["raio"] + 0.3, planeta["raio"] + 1.5, ANEIS_SATURNO_CFG["tex_id"])
                glPopMatrix()
            
            glPopMatrix()

        glDisable(GL_TEXTURE_2D)
        
        tempo_animacao += 0.5
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()