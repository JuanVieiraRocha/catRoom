import ctypes

import glm
import numpy as np
from OpenGL.GL import *

VERT = """
#version 330 core
layout(location = 0) in vec3 aPos;
layout(location = 1) in vec3 aNormal;
layout(location = 2) in vec2 aUV;
uniform mat4 uModel, uView, uProj;
out vec3 vPos;
out vec3 vNormal;
out vec2 vUV;
void main() {
    vec4 mundo = uModel * vec4(aPos, 1.0);
    vPos = mundo.xyz;
    vNormal = mat3(transpose(inverse(uModel))) * aNormal;
    vUV = aUV;
    gl_Position = uProj * uView * mundo;
}
"""

FRAG = """
#version 330 core
struct Luz { vec3 posicao; vec3 cor; };
struct Material { vec3 cor; float especular; float brilho; };
in vec3 vPos;
in vec3 vNormal;
in vec2 vUV;
uniform Luz uLuz;
uniform vec3 uLuzAmbiente;
uniform Material uMaterial;
uniform vec3 uViewPos;
uniform bool uUsarTextura;
uniform sampler2D uTextura;
out vec4 FragColor;
void main() {
    vec3 base = uUsarTextura ? texture(uTextura, vUV).rgb : uMaterial.cor;
    vec3 n = normalize(vNormal);
    vec3 l = normalize(uLuz.posicao - vPos);
    vec3 v = normalize(uViewPos - vPos);
    vec3 r = reflect(-l, n);
    vec3 ambiente = uLuzAmbiente * base;
    vec3 difusa   = max(dot(n, l), 0.0) * uLuz.cor * base;
    vec3 espec    = uMaterial.especular * pow(max(dot(v, r), 0.0), uMaterial.brilho) * uLuz.cor;
    FragColor = vec4(ambiente + difusa + espec, 1.0);
}
"""


class Shader:
    def __init__(self, vert=VERT, frag=FRAG):
        self.id = glCreateProgram()
        glAttachShader(self.id, self._compilar(vert, GL_VERTEX_SHADER))
        glAttachShader(self.id, self._compilar(frag, GL_FRAGMENT_SHADER))
        glLinkProgram(self.id)
        if not glGetProgramiv(self.id, GL_LINK_STATUS):
            raise RuntimeError(glGetProgramInfoLog(self.id).decode())
        self._locs = {}

    @staticmethod
    def _compilar(src, tipo):
        s = glCreateShader(tipo)
        glShaderSource(s, src)
        glCompileShader(s)
        if not glGetShaderiv(s, GL_COMPILE_STATUS):
            raise RuntimeError(glGetShaderInfoLog(s).decode())
        return s

    def usar(self):
        glUseProgram(self.id)

    def _loc(self, nome):
        if nome not in self._locs:
            self._locs[nome] = glGetUniformLocation(self.id, nome)
        return self._locs[nome]

    def mat4(self, nome, m):
        glUniformMatrix4fv(self._loc(nome), 1, GL_FALSE, glm.value_ptr(m))

    def vec3(self, nome, v):
        glUniform3f(self._loc(nome), *v)

    def float(self, nome, x):
        glUniform1f(self._loc(nome), x)

    def bool(self, nome, b):
        glUniform1i(self._loc(nome), int(b))

    def material(self, cor, especular=0.1, brilho=8.0):
        self.vec3("uMaterial.cor", cor)
        self.float("uMaterial.especular", especular)
        self.float("uMaterial.brilho", brilho)


class Cubo:
    
    def __init__(self):
        faces = [  # normal, eixo u, eixo v  (u x v = normal)
            ((0, 0, 1), (1, 0, 0), (0, 1, 0)), ((0, 0, -1), (-1, 0, 0), (0, 1, 0)),
            ((1, 0, 0), (0, 0, -1), (0, 1, 0)), ((-1, 0, 0), (0, 0, 1), (0, 1, 0)),
            ((0, 1, 0), (1, 0, 0), (0, 0, -1)), ((0, -1, 0), (1, 0, 0), (0, 0, 1)),
        ]
        uvs = [(0, 0), (1, 0), (1, 1), (0, 1)]
        dados = []
        for n, u, v in faces:
            n, u, v = map(np.array, (n, u, v))
            c = n * 0.5
            cantos = [c - u / 2 - v / 2, c + u / 2 - v / 2, c + u / 2 + v / 2, c - u / 2 + v / 2]
            for i in (0, 1, 2, 0, 2, 3):
                dados += [*cantos[i], *n, *uvs[i]]
        verts = np.array(dados, dtype=np.float32)
        self.n = len(verts) // 8

        self.vao = glGenVertexArrays(1)
        vbo = glGenBuffers(1)
        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, verts.nbytes, verts, GL_STATIC_DRAW)
        passo = 8 * 4
        for loc, tam, off in ((0, 3, 0), (1, 3, 12), (2, 2, 24)):
            glVertexAttribPointer(loc, tam, GL_FLOAT, GL_FALSE, passo, ctypes.c_void_p(off))
            glEnableVertexAttribArray(loc)
        glBindVertexArray(0)

    def desenhar(self, shader, modelo):
        shader.mat4("uModel", modelo)
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.n)


class MalhaOBJ:
    def __init__(self, cena):
        self.partes = []

        for mesh in cena.meshes.values():
            for material in mesh.materials:
                dados = np.asarray(material.vertices, dtype=np.float32)
                if dados.size == 0:
                    continue

                campos = {}
                deslocamento = 0
                for campo in material.vertex_format.split("_"):
                    tipo = campo[0]
                    quantidade = int(campo[1:-1])
                    campos[tipo] = (deslocamento, quantidade)
                    deslocamento += quantidade

                if deslocamento == 0 or dados.size % deslocamento != 0:
                    raise ValueError(
                        f"Formato de vértices inválido: {material.vertex_format}"
                    )

                dados = dados.reshape(-1, deslocamento)
                if "V" not in campos or campos["V"][1] != 3:
                    raise ValueError(
                        f"Esperava posições V3F; recebi {material.vertex_format}"
                    )

                inicio, tamanho = campos["V"]
                posicoes = dados[:, inicio:inicio + tamanho]

                if "N" in campos and campos["N"][1] == 3:
                    inicio, tamanho = campos["N"]
                    normais = dados[:, inicio:inicio + tamanho]
                else:
                    if len(posicoes) % 3 != 0:
                        raise ValueError(
                            "A malha sem normais não contém triângulos completos"
                        )

                    triangulos = posicoes.reshape(-1, 3, 3)
                    normais_face = np.cross(
                        triangulos[:, 1] - triangulos[:, 0],
                        triangulos[:, 2] - triangulos[:, 0],
                    )
                    comprimentos = np.linalg.norm(
                        normais_face, axis=1, keepdims=True
                    )
                    normais_face = np.divide(
                        normais_face,
                        comprimentos,
                        out=np.zeros_like(normais_face),
                        where=comprimentos != 0,
                    )
                    normais = np.repeat(normais_face, 3, axis=0)

                if "T" in campos and campos["T"][1] >= 2:
                    inicio, _ = campos["T"]
                    uv = dados[:, inicio:inicio + 2]
                else:
                    uv = np.zeros((len(posicoes), 2), dtype=np.float32)

                vertices = np.concatenate(
                    (posicoes, normais, uv), axis=1
                ).astype(np.float32, copy=False)
                cor = np.asarray(material.diffuse, dtype=np.float32)[:3]
                if cor.shape != (3,):
                    raise ValueError(
                        f"Cor difusa inválida no material {material.name}: {cor}"
                    )

                vao = glGenVertexArrays(1)
                vbo = glGenBuffers(1)
                glBindVertexArray(vao)
                glBindBuffer(GL_ARRAY_BUFFER, vbo)
                glBufferData(
                    GL_ARRAY_BUFFER,
                    vertices.nbytes,
                    vertices,
                    GL_STATIC_DRAW,
                )

                passo = 8 * vertices.itemsize
                for local, tamanho, deslocamento_bytes in (
                    (0, 3, 0),
                    (1, 3, 12),
                    (2, 2, 24),
                ):
                    glVertexAttribPointer(
                        local,
                        tamanho,
                        GL_FLOAT,
                        GL_FALSE,
                        passo,
                        ctypes.c_void_p(deslocamento_bytes),
                    )
                    glEnableVertexAttribArray(local)

                glBindVertexArray(0)
                self.partes.append((vao, len(vertices), tuple(cor)))

    def desenhar(self, shader, modelo):
        shader.mat4("uModel", modelo)
        for vao, quantidade, cor in self.partes:
            shader.material(cor)
            glBindVertexArray(vao)
            glDrawArrays(GL_TRIANGLES, 0, quantidade)
        glBindVertexArray(0)
