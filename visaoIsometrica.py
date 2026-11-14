import math

import glfw
from OpenGL.GL import *
import glm
import loadObj
from malha import MalhaOBJ, Shader
import projecao


def main():
    if not glfw.init():
        raise RuntimeError("Não foi possível inicializar o GLFW")

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)
    janela = glfw.create_window(1000, 700, "Quarto - visão isométrica", None, None)
    if not janela:
        glfw.terminate()
        raise RuntimeError("Não foi possível criar a janela OpenGL")

    glfw.make_context_current(janela)
    glfw.swap_interval(1)
    glEnable(GL_DEPTH_TEST)

    shader = Shader()
    vertices, uvs, normais = loadObj.load_obj("objects/Quarto.obj")
    quarto = MalhaOBJ(vertices, uvs, normais)

    limites_min = vertices.min(axis=0)
    limites_max = vertices.max(axis=0)
    escala_x = 8.0 / (limites_max[0] - limites_min[0])
    escala_y = 0.5
    escala_z = 8.0 / (limites_max[2] - limites_min[2])

    posicao_quarto = glm.vec3(
        -(limites_min[0] + limites_max[0]) * escala_x / 2,
        -limites_min[1] * escala_y,
        -(limites_min[2] + limites_max[2]) * escala_z / 2,
    )
    modelo_quarto = glm.translate(posicao_quarto) * glm.scale(
        glm.mat4(1), glm.vec3(escala_x, escala_y, escala_z)
    )

    # Câmera
    alvo = [3.5,(limites_max[1] - limites_min[1]) * escala_y / 2, 3.5]
    angulo_camera = math.pi / 4
    raio_camera = math.hypot(5.0, 5.0)
    altura_camera = 5.0
    olho = [
        alvo[0] + raio_camera * math.sin(angulo_camera),
        alvo[1] + altura_camera,
        alvo[2] + raio_camera * math.cos(angulo_camera),
    ]
    tempo_anterior = glfw.get_time()
    altura_visao = 22.0
    velocidade_zoom = 12.0
    altura_visao_min = 5.0
    altura_visao_max = 40.0

    while not glfw.window_should_close(janela):
        glfw.poll_events()
        tempo_atual = glfw.get_time()
        delta_tempo = min(tempo_atual - tempo_anterior, 0.05)
        tempo_anterior = tempo_atual
        olho, alvo = projecao.moverCamera(janela, olho, alvo, delta_tempo)
        if glfw.get_key(janela, glfw.KEY_W) == glfw.PRESS:
            altura_visao -= velocidade_zoom * delta_tempo
        if glfw.get_key(janela, glfw.KEY_S) == glfw.PRESS:
            altura_visao += velocidade_zoom * delta_tempo
        altura_visao = max(altura_visao_min, min(altura_visao, altura_visao_max))
        if glfw.get_key(janela, glfw.KEY_LEFT) == glfw.PRESS:
            angulo_camera -= 1.5 * delta_tempo
        if glfw.get_key(janela, glfw.KEY_RIGHT) == glfw.PRESS:
            angulo_camera += 1.5 * delta_tempo
        olho = [
            alvo[0] + raio_camera * math.sin(angulo_camera),
            alvo[1] + altura_camera,
            alvo[2] + raio_camera * math.cos(angulo_camera),
        ]

        largura, altura = glfw.get_framebuffer_size(janela)
        if largura == 0 or altura == 0:
            continue

        glViewport(0, 0, largura, altura)
        glClearColor(0.10, 0.22, 0.07, 1.0) # rgba(26, 57, 19, 0.8)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        aspect_ratio = largura / altura
        projecao_isometrica = glm.ortho(
            -altura_visao * aspect_ratio / 2,
            altura_visao * aspect_ratio / 2,
            -altura_visao / 2,
            altura_visao / 2,
            0.1,
            100.0,
        )
        matriz_view = glm.lookAt(
            glm.vec3(*olho), glm.vec3(*alvo), glm.vec3(0, 1, 0)
        )

        shader.usar()
        shader.mat4("uView", matriz_view)
        shader.mat4("uProj", projecao_isometrica)
        shader.vec3("uViewPos", olho)
        shader.vec3("uLuz.posicao", (0.0, 5.0, 0.0))
        shader.vec3("uLuz.cor", (1.0, 1.0, 1.0))
        shader.vec3("uLuzAmbiente", (0.35, 0.35, 0.4))
        shader.bool("uUsarTextura", False)


        shader.material((0.75, 0.72, 0.62), 0.25, 10.0)
        quarto.desenhar(shader, modelo_quarto)

        glfw.swap_buffers(janela)

    glfw.terminate()


if __name__ == "__main__":
    main()
