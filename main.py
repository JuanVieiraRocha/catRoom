import criandoObjetos
import projecao
import OpenGL.GL as openGL
import glfw
import numpy as np
from math import radians
import loadObj
import glm

vaoId = 0
shaderId = 0
matrizView = None
vertices = []
qtdDeVertices = 0

eye = [0.4, 30.0, 25.0]
at = [0.4, 0.6, -0.05]
up = [0.0, 1.0, 0.0]


def init():
    global vaoId, shaderId, matrizView, vertices, qtdDeVertices, eye, at, up

    vertices, uvs, normals = loadObj.load_obj('objects/Quarto.obj')
    vaoId = criandoObjetos.abrindoVao(1)
    qtdDeVertices = len(vertices)
    criandoObjetos.abrindoVbo(1, vertices, openGL.GL_STATIC_DRAW, 0, 3)
    openGL.glEnable(openGL.GL_DEPTH_TEST)


    # Aplicando shaders e matriz de visualização
    shaderId = criandoObjetos.shaderFacilitado(criandoObjetos.lendoArquivoGlsl(
        # Deixa o chão preto
        'chao_vertexShader.glsl'), criandoObjetos.lendoArquivoGlsl('chao_fragmentShader.glsl'), shaderId)
    matrizView = projecao.olhar_para(
        eye,
        at,
        up,
    )
    


def render():
    # Configurações para projeção
    largura, altura = glfw.get_framebuffer_size(window)  # Garante o aspect Ratio
    if largura == 0 or altura == 0:
        return

    openGL.glViewport(0, 0, largura, altura)

    openGL.glUseProgram(shaderId)
    # Depois do Shader Aplicado, como devem ser calculadas as posições
    matrizProjecao = projecao.perspectiva(
        radians(75.0),
        largura / altura,
        0.1,
        50.0,
    )

    localMatriz = openGL.glGetUniformLocation(shaderId, 'u_view_projection')
    matrizViewProjecao = matrizProjecao @ matrizView
    openGL.glUniformMatrix4fv(
        localMatriz,
        1,
        openGL.GL_FALSE,
        matrizViewProjecao.flatten(order='F'),
    )
    openGL.glBindVertexArray(vaoId)
    openGL.glDrawArrays(openGL.GL_TRIANGLES, 0, qtdDeVertices)
    openGL.glBindVertexArray(0)
    openGL.glUseProgram(0)

    openGL.glMatrixMode(openGL.GL_PROJECTION)
    openGL.glLoadMatrixf(matrizProjecao.astype(np.float32).flatten(order="F"))

    openGL.glMatrixMode(openGL.GL_MODELVIEW)
    openGL.glLoadMatrixf(matrizView.astype(np.float32).flatten(order="F"))

    # criandoObjetos.objetos()  # Desenha os objetos 3D


def main():  # a inicialização da janela e do loop principal do programa. Precisam ficar aqui, pois sempre precisam estar em movimento
    global window, matrizView, eye, at
    glfw.init()
    window = glfw.create_window(
        500, 500, 'catRoom - Um Cozy gato de Jogos', None, None)
    glfw.make_context_current(window)
    criandoObjetos.corDeFundo(1, 1, 1, 1)
    openGL.glEnable(openGL.GL_DEPTH_TEST)
    init()
    tempoAnterior = glfw.get_time()
    while not glfw.window_should_close(window):
        glfw.poll_events()
        tempoAtual = glfw.get_time()
        deltaTempo = tempoAtual - tempoAnterior
        tempoAnterior = tempoAtual
        eye, at = projecao.moverCamera(window, eye, at, deltaTempo)
        matrizView = projecao.olhar_para(eye, at, up)
        criandoObjetos.limpaBuffer()
        render()
        glfw.swap_buffers(window)
    glfw.terminate()


main()
