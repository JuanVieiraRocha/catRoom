import OpenGL.GL as openGL
import OpenGL.GL.shaders as gls
import numpy as np
import ctypes
from loadObj import loadObj

catBed = loadObj(obj_path=".\objects\CatBed.obj",
                 position=(0.4, 1.0, 0.4), scale=(0.5, 0.5, 0.5))
mouse = loadObj(obj_path=".\objects\model.obj", position=(0.4, 1.05, 0.4), scale=(0.2, 0.2, 0.2))


def corDeFundo(r, g, b, a):
    openGL.glClearColor(r, g, b, a)


def abrindoVao(id):
    vaoId = openGL.glGenVertexArrays(id)
    openGL.glBindVertexArray(vaoId)
    return vaoId


def abrindoVbo(id, vertices, tipoDeDesenhoDoOpenGL, codigoDeObj, dimensoesVertice):
    vboId = openGL.glGenBuffers(id)
    openGL.glBindBuffer(openGL.GL_ARRAY_BUFFER, vboId)
    openGL.glBindBuffer(openGL.GL_ARRAY_BUFFER, vboId)
    openGL.glBufferData(openGL.GL_ARRAY_BUFFER,
                        vertices.nbytes, vertices, tipoDeDesenhoDoOpenGL)
    openGL.glVertexAttribPointer(codigoDeObj,
                                 dimensoesVertice,
                                 openGL.GL_FLOAT,
                                 openGL.GL_FALSE,
                                 dimensoesVertice*4,
                                 ctypes.c_void_p(0))
    openGL.glEnableVertexAttribArray(codigoDeObj)


def lendoArquivoGlsl(caminhoDoArquivo):
    with open(caminhoDoArquivo, 'r') as file:
        source = file.read()
    print(f'Arquivo de nome: {caminhoDoArquivo} foi lido')
    print(source)
    return source


def limpaBuffer():
    openGL.glClear(openGL.GL_COLOR_BUFFER_BIT | openGL.GL_DEPTH_BUFFER_BIT)


def shaderFacilitado(arquivoVertex, arquivoFragment, shaderId):
    vsId = gls.compileShader(arquivoVertex, openGL.GL_VERTEX_SHADER)
    fsId = gls.compileShader(arquivoFragment, openGL.GL_FRAGMENT_SHADER)
    shaderId = gls.compileProgram(vsId, fsId)
    return shaderId


# CRIAÇÃO DE OBJETOS
def criarChao(matriz, xinit, xend, y, zinit, zend):
    matriz = [
        [xinit, y, zinit],
        [xend, y, zinit],
        [xinit, y, zend],
        [xend, y, zend],
    ]
    return matriz


def criarTriangulo(matriz, altura, comprimento):
    matriz = [
        [comprimento/2, altura],
        [comprimento, 0],
        [-comprimento/2, 0],
    ]
    return matriz


def objetos():
    catBed.draw()
    mouse.draw()