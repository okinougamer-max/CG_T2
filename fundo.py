import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import random
import os
from PIL import Image


def encontrar_arquivo(nome_arquivo):
    if os.path.exists(nome_arquivo): return nome_arquivo
    
    caminho_assets = os.path.join("assets", nome_arquivo)
    if os.path.exists(caminho_assets): return caminho_assets
    
    dir_atual = os.path.dirname(os.path.abspath(__file__))
    caminho_completo = os.path.join(dir_atual, "assets", nome_arquivo)
    if os.path.exists(caminho_completo): return caminho_completo
    
    return None

def gerar_textura_procedural(cor_rgb, largura=64, altura=64):
    data = bytearray()
    r_base, g_base, b_base = [int(c * 255) for c in cor_rgb]
    for _ in range(altura):
        for _ in range(largura):
            noise = random.randint(-30, 30)
            data.extend([
                max(0, min(255, r_base + noise)), 
                max(0, min(255, g_base + noise)), 
                max(0, min(255, b_base + noise)), 
                255
            ]) 
    return data, largura, altura

def load_texture(filename, cor_placeholder_rgb=None):
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    
    img_data, width, height = None, 0, 0
    caminho_real = encontrar_arquivo(filename)
    loaded = False

    if caminho_real:
        try:
            img = Image.open(caminho_real).convert("RGBA")
            img_data = img.tobytes("raw", "RGBA", 0, -1)
            width, height = img.size
            loaded = True
        except Exception as e:
            print(f"Erro ao carregar textura {filename}: {e}")
    
    if not loaded:
        print(f"Usando textura procedural para: {filename}")
        if cor_placeholder_rgb is None: cor_placeholder_rgb = (0.5, 0.5, 0.5)
        img_data, width, height = gerar_textura_procedural(cor_placeholder_rgb)
    
    if img_data:
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
    
    return texture_id

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

NAVE_CFG = {"tex_file": "nave.jpg", "tex_id": None, "cor_base": (0.5, 0.5, 0.5)}
METEORO_CFG = {"tex_file": "meteoro.jpg", "tex_id": None, "cor_base": (0.4, 0.4, 0.4)}

def desenhar_esfera_texturizada(raio, texture_id):
    glColor3f(1.0, 1.0, 1.0)
    
    if texture_id: 
        glBindTexture(GL_TEXTURE_2D, texture_id)
        quadric = gluNewQuadric()
        gluQuadricTexture(quadric, GL_TRUE) 
        gluSphere(quadric, raio, 20, 20)
        gluDeleteQuadric(quadric)
    else:
        quadric = gluNewQuadric()
        gluSphere(quadric, raio, 20, 20)
        gluDeleteQuadric(quadric)

def desenhar_anel_texturizado(raio_interno, raio_externo, texture_id):
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(1.0, 1.0, 1.0, 0.9) 
    
    if texture_id: glBindTexture(GL_TEXTURE_2D, texture_id)
    
    quadric = gluNewQuadric()
    gluQuadricTexture(quadric, GL_TRUE)
    gluDisk(quadric, raio_interno, raio_externo, 40, 1)
    gluDeleteQuadric(quadric)
    glDisable(GL_BLEND)

def init_opengl():
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL) 
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
    glShadeModel(GL_SMOOTH)

def init_all_textures():
    glEnable(GL_TEXTURE_2D)
    
    print("Carregando texturas...")
    SOL_CFG["tex_id"] = load_texture(SOL_CFG["tex_file"], SOL_CFG["cor_base"])
    LUA_TERRA["tex_id"] = load_texture(LUA_TERRA["tex_file"], LUA_TERRA["cor_base"])
    ANEIS_SATURNO_CFG["tex_id"] = load_texture(ANEIS_SATURNO_CFG["tex_file"], ANEIS_SATURNO_CFG["cor_base"])
    
    NAVE_CFG["tex_id"] = load_texture(NAVE_CFG["tex_file"], NAVE_CFG["cor_base"])
    METEORO_CFG["tex_id"] = load_texture(METEORO_CFG["tex_file"], METEORO_CFG["cor_base"])

    for p in PLANETAS:
        p["tex_id"] = load_texture(p["tex_file"], p["cor_base"])
    print("Texturas carregadas.")

def desenhar_cenario(tempo_animacao):
    glPushMatrix()
    glEnable(GL_TEXTURE_2D)

    glPushMatrix()
    glMaterialfv(GL_FRONT, GL_EMISSION, [1.0, 1.0, 1.0, 1.0]) 
    desenhar_esfera_texturizada(SOL_CFG["raio"], SOL_CFG["tex_id"]) 
    glMaterialfv(GL_FRONT, GL_EMISSION, [0.0, 0.0, 0.0, 1.0])
    glPopMatrix()

    for planeta in PLANETAS:
        glPushMatrix() 
        angulo_planeta = (tempo_animacao * planeta["vel"]) % 360
        glRotate(angulo_planeta, 0, 1, 0)
        glTranslate(planeta["dist"], 0, 0)
        
        glPushMatrix() 
        glRotate(tempo_animacao * 2, 0, 1, 0) 
        desenhar_esfera_texturizada(planeta["raio"], planeta["tex_id"])
        glPopMatrix()

        if planeta["nome"] == "Terra":
            glPushMatrix()
            glRotate((tempo_animacao * LUA_TERRA["vel"]) % 360, 0.1, 1, 0) 
            glTranslate(LUA_TERRA["dist"], 0, 0)
            desenhar_esfera_texturizada(LUA_TERRA["raio"], LUA_TERRA["tex_id"])
            glPopMatrix()

        if planeta["nome"] == "Saturno":
            glPushMatrix()
            glRotate(45, 1, 0, 0) 
            desenhar_anel_texturizado(planeta["raio"] + 0.3, planeta["raio"] + 1.5, ANEIS_SATURNO_CFG["tex_id"])
            glPopMatrix()
        
        glPopMatrix()
    
    glDisable(GL_TEXTURE_2D)
    glPopMatrix()