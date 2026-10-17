import criandoObjetos
import OpenGL.GL as openGL
import glfw
import numpy as np

vaoId = 0
shaderId = 0
vertices = []
qtdDeVertices = 0

def init():
    global vaoId, shaderId, vertices, qtdDeVertices
    # Criando chão 3D
    vertices = criandoObjetos.criarChao(vertices, 0.2, 0.6, -0.3, 0.2, 0.6)
    dimensoesVertice = len(vertices[0])
    qtdDeVertices = len(vertices)
    vaoId = criandoObjetos.abrindoVao(1) # Boa prática, fechar isso aqui com glBindVertexArray(0) depois de criar o VAO
    criandoObjetos.abrindoVbo(1, np.array(vertices, np.dtype(np.float32)), openGL.GL_STATIC_DRAW, 0, dimensoesVertice)

    # testando Triangulo 2d
    # vertices = criandoObjetos.criarTriangulo(vertices, 0.3, 0.6)
    # dimensoesVertice = len(vertices[0])
    # print(f'Essa é a dimensão de cada vértice: {dimensoesVertice}')
    # qtdDeVertices = len(vertices)
    # print(f'essa é a quantidade de vértices: {qtdDeVertices}')
    # vaoId = criandoObjetos.abrindoVao(1)

    # criandoObjetos.abrindoVbo(1, np.array(vertices, np.dtype(np.float32)), openGL.GL_STATIC_DRAW, 0, dimensoesVertice)

    openGL.glBindBuffer(openGL.GL_ARRAY_BUFFER, 0) # Fehcando VBO
    openGL.glBindVertexArray(0)                    # Fechando VAO

    # Aplicando shaders no chão
    shaderId = criandoObjetos.shaderFacilitado(criandoObjetos.lendoArquivoGlsl('chao_vertexShader.glsl'), criandoObjetos.lendoArquivoGlsl('chao_fragmentShader.glsl'), shaderId) # Deixa o chão preto
    
    # Aplicando Shaders no triangulo
    # shaderId = criandoObjetos.shaderFacilitado(criandoObjetos.lendoArquivoGlsl('05_vertexShader.glsl'), criandoObjetos.lendoArquivoGlsl('05_fragmentShader.glsl'), shaderId)
    # print(f'Esse é o shaderId: {shaderId}')


def render():
    openGL.glUseProgram(shaderId)
    openGL.glBindVertexArray(vaoId)
    openGL.glDrawArrays(openGL.GL_QUADS, 0, qtdDeVertices)
    openGL.glBindVertexArray(0)
    openGL.glUseProgram(0)
    



def main(): # a inicialização da janela e do loop principal do programa. Precisam ficar aqui, pois sempre precisam estar em movimento
    glfw.init()
    window = glfw.create_window(500, 500, 'catRoom - Um Cozy gato de Jogos', None, None)
    glfw.make_context_current(window)
    criandoObjetos.corDeFundo(1, 1, 1, 1)
    init()
    while not glfw.window_should_close(window):
        glfw.poll_events()
        criandoObjetos.limpaBuffer()
        render()
        glfw.swap_buffers(window)
    glfw.terminate()

main()