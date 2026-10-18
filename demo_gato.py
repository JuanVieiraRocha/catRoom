"""
  W  andar até um ponto aleatório
  S  sentar / levantar
  F  comer
  C  carinho
  B  brincar
  1  laranja    2  cinza        3  frajola
  Setas esquerda/direita  girar a câmera
  ESC  sair
"""
import math
import random

import glfw
import glm
from OpenGL.GL import *

from gato import Gato
from malha import Cubo, Shader


def main():
    glfw.init()
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)
    janela = glfw.create_window(1000, 650, "Gato", None, None)
    glfw.make_context_current(janela)
    glfw.swap_interval(1)
    glEnable(GL_DEPTH_TEST)

    shader = Shader()
    cubo = Cubo()
    gato = Gato(cubo)
    dinheiro = 0
    angulo_camera = 0.8

    def tecla(janela, key, scancode, acao, mods):
        nonlocal dinheiro
        if acao != glfw.PRESS:
            return
        if key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(janela, True)
        elif key == glfw.KEY_W:
            gato.ir_para(random.uniform(-1, 1), random.uniform(-1, 1))
        elif key == glfw.KEY_S:
            gato.sentar()
        elif key == glfw.KEY_F:
            dinheiro += gato.interagir("comendo")
        elif key == glfw.KEY_C:
            dinheiro += gato.interagir("carinho")
        elif key == glfw.KEY_B:
            dinheiro += gato.interagir("brincando")
        elif key == glfw.KEY_1:
            gato.trocar_pelagem("laranja")
        elif key == glfw.KEY_2:
            gato.trocar_pelagem("cinza")
        elif key == glfw.KEY_3:
            gato.trocar_pelagem("frajola")

    glfw.set_key_callback(janela, tecla)
    anterior = glfw.get_time()

    while not glfw.window_should_close(janela):
        agora = glfw.get_time()
        dt = min(agora - anterior, 0.05)
        anterior = agora

        if glfw.get_key(janela, glfw.KEY_LEFT) == glfw.PRESS:
            angulo_camera -= 1.5 * dt
        if glfw.get_key(janela, glfw.KEY_RIGHT) == glfw.PRESS:
            angulo_camera += 1.5 * dt

        gato.update(dt)

        w, h = glfw.get_framebuffer_size(janela)
        glViewport(0, 0, w, h)
        glClearColor(0.75, 0.82, 0.88, 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # câmera girando em volta do gato
        alvo = gato.posicao + glm.vec3(0, 0.2, 0)
        olho = alvo + glm.vec3(1.4 * math.sin(angulo_camera), 0.6, 1.4 * math.cos(angulo_camera))
        shader.usar()
        shader.mat4("uView", glm.lookAt(olho, alvo, glm.vec3(0, 1, 0)))
        shader.mat4("uProj", glm.perspective(glm.radians(45), w / max(h, 1), 0.05, 50))
        shader.vec3("uViewPos", olho)
        shader.vec3("uLuz.posicao", (1.2, 2.5, 1.5))
        shader.vec3("uLuz.cor", (1, 1, 1))
        shader.vec3("uLuzAmbiente", (0.35, 0.35, 0.4))
        shader.bool("uUsarTextura", False)

        shader.material((0.55, 0.42, 0.32))  # chão
        chao = glm.scale(glm.translate(glm.mat4(1), glm.vec3(0, -0.025, 0)), glm.vec3(3, 0.05, 3))
        cubo.desenhar(shader, chao)

        gato.desenhar(shader)

        glfw.set_window_title(janela, f"Gato  |  {gato.estado}  |  dinheiro: ${dinheiro}")
        glfw.swap_buffers(janela)
        glfw.poll_events()

    glfw.terminate()


if __name__ == "__main__":
    main()