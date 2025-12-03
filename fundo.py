# fundo.py (Versão Modular)
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import random
import os

# Tenta importar PIL
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("AVISO: Biblioteca Pillow (PIL) não encontrada.")

# ================= CONFIGURAÇÕES GLOBAIS =================
PLANETAS = [
    {"nome": "Mercurio", "raio": 0.4, "dist": 6,  "vel": 4.5, "cor_base": (0.7, 0.7, 0.7), "tex_file": "mercurio.jpg", "tex_id": None},
    {"nome": "Venus",    "raio": 0.6, "dist": 9,  "vel": 3.5, "cor_base": (1.0, 0.8, 0.2), "tex_file": "venus.png", "tex_id": None},
    {"nome": "Terra",    "raio": 0.6, "dist": 12, "vel": 2.5, "cor_base": (0.0, 0.0, 1.0), "tex_file": "terra.jpg", "tex_id": None},
    {"nome": "Marte",    "raio": 0.5, "dist": 15, "vel": 2.0, "cor_base": (1.0, 0.2, 0.0), "tex_file": "marte.jpg", "tex_id": None},
    {"nome": "Jupiter",  "raio": 1.4, "dist": 22, "vel": 1.2, "cor_base": (0.9, 0.6, 0.4), "tex_file": "jupiter.png", "tex_id": None},
    {"nome": "Saturno",  "raio": 1.2, "dist": 30, "vel": 0.9, "cor_base": (0.8, 0.7, 0.5), "tex_file": "saturno.png", "tex_id": None},
    {"nome": "Urano",    "raio": 0.9, "dist": 38, "vel": 0.6, "cor_base": (0.4, 0.9, 0.9), "tex_file": "urano.png", "tex_id": None},
    {"nome": "Netuno",   "raio": 0.9, "dist": 45, "vel": 0.4, "cor_base": (0.1, 0.1, 0.8), "tex_file": "netuno.png", "tex_id": None},
]

LUA_TERRA = {"raio": 0.2, "dist": 1.8, "vel": 10.0, "cor_base": (0.8, 0.8, 0.8), "tex_file": "lua.png", "tex_id": None}
SOL_CFG = {"raio": 3.5, "cor_base": (1.0, 0.8, 0.2), "tex_file": "sol.png", "tex_id": None}
ANEIS_SATURNO_CFG = {"tex_file": "anelSaturno.png", "tex_id": None, "cor_base": (0.7, 0.6, 0.4)}

# ================= FUNÇÕES DE UTILIDADE =================
def encontrar_arquivo(nome_arquivo):
    if os.path.exists(nome_arquivo): return nome_arquivo
    caminho_assets = os.path.join("assets", nome_arquivo)
    if os.path.exists(caminho_assets): return caminho_assets
    # Fallback
    nome_sem_ext, ext = os.path.splitext(nome_arquivo)
    alternativas = [nome_sem_ext + ".png", nome_sem_ext + ".jpg", 
                    os.path.join("assets", nome_sem_ext + ".png"), os.path.join("assets", nome_sem_ext + ".jpg")]
    for alt in alternativas:
        if os.path.exists(alt): return alt
    return None

def gerar_textura_procedural(cor_rgb, largura=64, altura=64):
    data = bytearray()
    r_base, g_base, b_base = [int(c * 255) for c in cor_rgb]
    for _ in range(altura):
        for _ in range(largura):
            noise = random.randint(-30, 30)
            data.extend([max(0, min(255, r_base+noise)), max(0, min(255, g_base+noise)), max(0, min(255, b_base+noise)), 255])
    return data, largura, altura

def load_texture(filename, cor_placeholder_rgb=None):
    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    
    img_data = None
    path = encontrar_arquivo(filename)
    if PIL_AVAILABLE and path:
        try:
            img = Image.open(path).convert("RGBA")
            img_data = img.tobytes("raw", "RGBA", 0, -1)
            w, h = img.size
        except: pass

    if not img_data and cor_placeholder_rgb:
        img_data, w, h = gerar_textura_procedural(cor_placeholder_rgb)

    if img_data:
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
    
    return tex_id

def init_all_textures():
    SOL_CFG["tex_id"] = load_texture(SOL_CFG["tex_file"], SOL_CFG["cor_base"])
    LUA_TERRA["tex_id"] = load_texture(LUA_TERRA["tex_file"], LUA_TERRA["cor_base"])
    ANEIS_SATURNO_CFG["tex_id"] = load_texture(ANEIS_SATURNO_CFG["tex_file"], ANEIS_SATURNO_CFG["cor_base"])
    for p in PLANETAS:
        p["tex_id"] = load_texture(p["tex_file"], p["cor_base"])

def init_opengl():
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
    glShadeModel(GL_SMOOTH)

# ================= FUNÇÃO DE DESENHO (INTERFACE PARA O GAME.PY) =================
def desenhar_esfera(raio, tex_id):
    glBindTexture(GL_TEXTURE_2D, tex_id)
    q = gluNewQuadric()
    gluQuadricTexture(q, GL_TRUE)
    gluSphere(q, raio, 32, 32)
    gluDeleteQuadric(q)

def desenhar_sistema_solar(tempo_animacao):
    """
    Desenha o sistema solar completo. Deve ser chamado dentro do loop do jogo.
    """
    glEnable(GL_TEXTURE_2D)
    
    # 1. Sol
    glPushMatrix()
    glLightfv(GL_LIGHT0, GL_POSITION, [0.0, 0.0, 0.0, 1.0])
    glMaterialfv(GL_FRONT, GL_EMISSION, [1.0, 1.0, 1.0, 1.0])
    glColor3f(1, 1, 1)
    desenhar_esfera(SOL_CFG["raio"], SOL_CFG["tex_id"])
    glMaterialfv(GL_FRONT, GL_EMISSION, [0.0, 0.0, 0.0, 1.0])
    glPopMatrix()

    # 2. Planetas
    for p in PLANETAS:
        glPushMatrix()
        glRotate((tempo_animacao * p["vel"]) % 360, 0, 1, 0)
        glTranslate(p["dist"], 0, 0)
        
        glPushMatrix()
        glRotate(tempo_animacao * 2, 0, 1, 0)
        desenhar_esfera(p["raio"], p["tex_id"])
        glPopMatrix()

        # Lua da Terra
        if p["nome"] == "Terra":
            glPushMatrix()
            glRotate((tempo_animacao * LUA_TERRA["vel"]) % 360, 0.1, 1, 0)
            glTranslate(LUA_TERRA["dist"], 0, 0)
            desenhar_esfera(LUA_TERRA["raio"], LUA_TERRA["tex_id"])
            glPopMatrix()

        # Anéis de Saturno
        if p["nome"] == "Saturno":
            glPushMatrix()
            glRotate(45, 1, 0, 0)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glColor4f(1, 1, 1, 0.9)
            glBindTexture(GL_TEXTURE_2D, ANEIS_SATURNO_CFG["tex_id"])
            q = gluNewQuadric(); gluQuadricTexture(q, GL_TRUE)
            gluDisk(q, p["raio"]+0.3, p["raio"]+1.5, 40, 1)
            gluDeleteQuadric(q)
            glDisable(GL_BLEND)
            glPopMatrix()

        glPopMatrix()
    
    glDisable(GL_TEXTURE_2D)

# Permite rodar sozinho para teste se necessário
if __name__ == "__main__":
    pygame.init()
    d = (800, 600)
    pygame.display.set_mode(d, DOUBLEBUF | OPENGL)
    gluPerspective(45, (d[0]/d[1]), 0.1, 200.0)
    gluLookAt(0, 40, 60, 0, 0, 0, 0, 1, 0)
    init_opengl()
    init_all_textures()
    t = 0
    clk = pygame.time.Clock()
    while True:
        for e in pygame.event.get(): 
            if e.type == QUIT: quit()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        desenhar_sistema_solar(t)
        t += 0.5
        pygame.display.flip()
        clk.tick(60)