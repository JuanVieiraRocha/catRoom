import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders as gls 
import numpy as np
import ctypes

vertices = [
    [-0.3 , -0.2],
    [ 0.0 ,  0.4],
    [ 0.3 , -0.2],
]
qtdVertices = len(vertices)

vaoId = 0
shaderId = 0

def criandoVAOeVBO():
    global vaoId, shaderId, vertices

    vertices = np.array(vertices, np.dtype(np.float32)) # Converte os vértices para um array numpy de float32

    vaoId = glGenVertexArrays(1) # Criando o VAO
    glBindVertexArray(vaoId) # ligando VAO


    # criando o VBO
    vboId = glGenBuffers(1)
    # Ativando o VBO
    glBindBuffer(GL_ARRAY_BUFFER, vboId)
    # Enviando informações do VBO
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
    glVertexAttribPointer(0, # Codigo definido pelo usuário
                          2, # Quantos elementos por vértice
                          GL_FLOAT, # Tipo dos valores no array 
                          GL_FALSE, # Se os valores de cor precisam ser normalizados
                          2*4, # Quantidade de atributos por vértice (2 floats * 4 bytes)
                          ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)

    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)

def shadersEncurtados():
    global shaderId
    with open('05_vertexShader.glsl', 'r') as file:
        vsSource = file.read()
        print("Arquivo lido: 05_vertexShader.glsl")
    # Codigo fonte Dos Shaders
    with open('05_fragmentShader.glsl', 'r') as file:
        fsSource = file.read()
        print("Arquivo lido: 05_fragmentShader.glsl")

    vsId = gls.compileShader(vsSource, GL_VERTEX_SHADER)
    fsId = gls.compileShader(fsSource, GL_FRAGMENT_SHADER)
    shaderId = gls.compileProgram(vsId, fsId)

def init():
    global shaderId, vaoId, vertices
    glClearColor(1, 1, 1, 1)
    criandoVAOeVBO()
    shadersEncurtados()

    # # Criar Shaders
    # with open('05_vertexShader.glsl', 'r') as file:
    #     vsSource = file.read()
    #     print("Arquivo lido: 05_vertexShader.glsl")
    # # Codigo fonte Dos Shaders
    # with open('05_fragmentShader.glsl', 'r') as file:
    #     fsSource = file.read()
    #     print("Arquivo lido: 05_fragmentShader.glsl")
    # # Criar objeto fragment Shader

    # # Config de shader vertex
    # vsId = glCreateShader(GL_VERTEX_SHADER)
    # glShaderSource(vsId, vsSource)
    # glCompileShader(vsId)
    # if not glGetShaderiv(vsId, GL_COMPILE_STATUS):
    #     info = glGetShaderInfoLog(vsId)
    #     print('Erro de Compilação no vertex Shader')
    #     print(info)



    # # Config de shader fragment
    # fsId = glCreateShader(GL_FRAGMENT_SHADER)
    # glShaderSource(fsId, fsSource)
    # glCompileShader(fsId)
    # if not glGetShaderiv(fsId, GL_COMPILE_STATUS):
    #     info = glGetShaderInfoLog(fsId)
    #     print('Erro de Compilação no fragment Shader')
    #     print(info)

    # # Criando o programa de shader
    # shaderId = glCreateProgram()

    # glAttachShader(shaderId, vsId)
    # glAttachShader(shaderId, fsId)
    # glLinkProgram(shaderId)

def render():
    glClear(GL_COLOR_BUFFER_BIT)
    glUseProgram(shaderId)
    glBindVertexArray(vaoId)
    glDrawArrays(GL_TRIANGLES, 
                 0,
                 qtdVertices)
    glBindVertexArray(0)
    glUseProgram(0)

def main():
    glfw.init()
    window = glfw.create_window(500, 500, "catRoom - Janela", None, None)
    glfw.make_context_current(window)
    init()
    while not glfw.window_should_close(window):
        glfw.poll_events()
        render()
        glfw.swap_buffers(window)
    glfw.terminate()


main()