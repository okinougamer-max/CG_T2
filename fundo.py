import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
import os
from PIL import Image

PLANETAS = [
    {"nome": "Mercurio", "raio": 0.4, "dist": 6,  "vel": 4.5, "tex": "mercurio.jpg", "id": None},
    {"nome": "Venus",    "raio": 0.6, "dist": 9,  "vel": 3.5, "tex": "venus.png",   "id": None},
    {"nome": "Terra",    "raio": 0.6, "dist": 12, "vel": 2.5, "tex": "terra.jpg",   "id": None},
    {"nome": "Marte",    "raio": 0.5, "dist": 15, "vel": 2.0, "tex": "marte.jpg",   "id": None},
    {"nome": "Jupiter",  "raio": 1.4, "dist": 22, "vel": 1.2, "tex": "jupiter.png", "id": None},
    {"nome": "Saturno",  "raio": 1.2, "dist": 30, "vel": 0.9, "tex": "saturno.png", "id": None},
    {"nome": "Urano",    "raio": 0.9, "dist": 38, "vel": 0.6, "tex": "urano.png",   "id": None},
    {"nome": "Netuno",   "raio": 0.9, "dist": 45, "vel": 0.4, "tex": "netuno.png",  "id": None},
]
LUA_TERRA = {"raio": 0.2, "dist": 1.8, "vel": 10.0, "tex": "lua.png", "id": None}
SOL_CFG = {"raio": 3.5, "tex": "sol.png", "id": None}
ANEIS_SATURNO = {"tex": "anelSaturno.png", "id": None}
NAVE_CFG = {"tex": "nave.jpg", "id": None}
METEORO_CFG = {"tex": "meteoro.jpg", "id": None}

def load_texture(filename):
    filepath = os.path.join("assets", filename)
    if not os.path.exists(filepath):
        print(f"Erro: {filename} não encontrado.")
        return None

    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    
    try:
        img = Image.open(filepath).convert("RGBA")
        img_data = img.tobytes("raw", "RGBA", 0, -1)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img.width, img.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
        return tex_id
    except Exception as e:
        print(f"Erro ao carregar textura {filename}: {e}")
        return None

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
    SOL_CFG["id"] = load_texture(SOL_CFG["tex"])
    LUA_TERRA["id"] = load_texture(LUA_TERRA["tex"])
    ANEIS_SATURNO["id"] = load_texture(ANEIS_SATURNO["tex"])
    NAVE_CFG["id"] = load_texture(NAVE_CFG["tex"])
    METEORO_CFG["id"] = load_texture(METEORO_CFG["tex"])
    for p in PLANETAS:
        p["id"] = load_texture(p["tex"])

def desenhar_esfera(raio, tex_id):
    quad = gluNewQuadric()
    if tex_id:
        glBindTexture(GL_TEXTURE_2D, tex_id)
        gluQuadricTexture(quad, GL_TRUE)
    gluSphere(quad, raio, 20, 20)
    gluDeleteQuadric(quad)

def desenhar_cenario(tempo):
    glPushMatrix()
    glEnable(GL_TEXTURE_2D)
    glColor3f(1, 1, 1)

    # Sol
    glPushMatrix()
    glMaterialfv(GL_FRONT, GL_EMISSION, [1, 1, 1, 1]) 
    desenhar_esfera(SOL_CFG["raio"], SOL_CFG["id"])
    glMaterialfv(GL_FRONT, GL_EMISSION, [0, 0, 0, 1])
    glPopMatrix()

    for p in PLANETAS:
        glPushMatrix() 
        glRotate((tempo * p["vel"]) % 360, 0, 1, 0)
        glTranslate(p["dist"], 0, 0)
        
        glPushMatrix() # Rotação do planeta
        glRotate(tempo * 2, 0, 1, 0) 
        desenhar_esfera(p["raio"], p["id"])
        glPopMatrix()

        if p["nome"] == "Terra": # Lua
            glPushMatrix()
            glRotate((tempo * LUA_TERRA["vel"]) % 360, 0.1, 1, 0) 
            glTranslate(LUA_TERRA["dist"], 0, 0)
            desenhar_esfera(LUA_TERRA["raio"], LUA_TERRA["id"])
            glPopMatrix()

        if p["nome"] == "Saturno": 
            glPushMatrix()
            glRotate(45, 1, 0, 0) 
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            if ANEIS_SATURNO["id"]: glBindTexture(GL_TEXTURE_2D, ANEIS_SATURNO["id"])
            q = gluNewQuadric()
            gluQuadricTexture(q, GL_TRUE)
            gluDisk(q, p["raio"] + 0.3, p["raio"] + 1.5, 40, 1)
            gluDeleteQuadric(q)
            glDisable(GL_BLEND)
            glPopMatrix()
        
        glPopMatrix()
    
    glDisable(GL_TEXTURE_2D)
    glPopMatrix()