import numpy as np
import glfw
import glm

def perspectiva(fov_y, aspect, near, far):
    matriz = glm.perspective(fov_y, aspect, near, far)
    return np.asarray(matriz, dtype=np.float32).copy()


def olhar_para(eye, at, up):
    matriz = glm.lookAt(
        glm.vec3(*eye),
        glm.vec3(*at),
        glm.vec3(*up),
    )
    return np.asarray(matriz, dtype=np.float32).copy()


def moverCamera(janela, eye, at, delta_tempo, velocidade=3.0):
    eye = np.asarray(eye, dtype=np.float32)
    at = np.asarray(at, dtype=np.float32)
    frente = at - eye
    frente[1] = 0.0
    frente /= np.linalg.norm(frente)
    direita = np.cross(frente, np.array([0.0, 1.0, 0.0], dtype=np.float32))

    deslocamento = np.zeros(3, dtype=np.float32)
    if glfw.get_key(janela, glfw.KEY_UP) == glfw.PRESS or glfw.get_key(janela, glfw.KEY_W) == glfw.PRESS:
        deslocamento += frente
    if glfw.get_key(janela, glfw.KEY_DOWN) == glfw.PRESS or glfw.get_key(janela, glfw.KEY_S) == glfw.PRESS:
        deslocamento -= frente
    if glfw.get_key(janela, glfw.KEY_RIGHT) == glfw.PRESS or glfw.get_key(janela, glfw.KEY_D) == glfw.PRESS:
        deslocamento += direita
    if glfw.get_key(janela, glfw.KEY_LEFT) == glfw.PRESS or glfw.get_key(janela, glfw.KEY_A) == glfw.PRESS:
        deslocamento -= direita

    comprimento = np.linalg.norm(deslocamento)
    if comprimento > 0.0:
        deslocamento *= velocidade * delta_tempo / comprimento

    novo_eye = eye + deslocamento
    novo_at = at + deslocamento
    return novo_eye.tolist(), novo_at.tolist()