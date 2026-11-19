import ctypes

import glm
import numpy as np
from OpenGL.GL import *
from criandoObjetos import abrindoVao, abrindoVbo
from loadObj import load_obj
from PIL import Image

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

POINTLIGHT = """
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

void main(){
    vec3 base = uUsarTextura ? texture(uTextura, vUV).rgb : uMaterial.cor;
    vec3 n = normalize(vNormal);
    vec3 l = normalize(uLuz.posicao - vPos);
    vec3 v = normalize(uViewPos - vPos);
    vec3 r = reflect(-l, n);
    vec3 ambiente = uLuzAmbiente * base
    vec3 difusa
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
    
    def sampler2D(self, nome, unidade):
        glUniform1i(self._loc(nome), unidade)

    def material(self, cor, especular=0.1, brilho=8.0):
        self.vec3("uMaterial.cor", cor)
        self.float("uMaterial.especular", especular)
        self.float("uMaterial.brilho", brilho)
class pointLight():
    pass


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
    def __init__(self, vertices, uvs, normais):
        self.vertices = vertices
        self.uvs = uvs
        self.normais = normais
        self.vao = glGenVertexArrays(1)
        vbo = glGenBuffers(1)


        dados = np.ascontiguousarray(
        np.concatenate((vertices, normais, uvs), axis=1),
        dtype=np.float32
)

        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, dados.nbytes, dados, GL_STATIC_DRAW)

        stride = 8 * 4
        for local, tamanho, deslocamento in (
            (0, 3, 0),   # posição
            (1, 3, 12),  # normal
            (2, 2, 24),  # UV
        ):
            glVertexAttribPointer(
                local, tamanho, GL_FLOAT, GL_FALSE,
                stride, ctypes.c_void_p(deslocamento)
            )
            glEnableVertexAttribArray(local)

        glBindVertexArray(0)

    def desenhar(self, shader, modelo):
        shader.mat4("uModel", modelo)
        glBindTextureUnit(0, self.texId)
        glBindTexture(GL_TEXTURE_2D, self.texId)
        shader.sampler2D("uTextura", 0)
        shader.bool("uUsarTextura", True)


        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, len(self.vertices))
        glBindVertexArray(0)
        pass
    def carregarTextura(self, caminhoImagem):
        img = Image.open(caminhoImagem) # carrega a imagem
        img = img.transpose(Image.FLIP_TOP_BOTTOM) # inverte a imagem verticalmente
        imgData = img.convert('RGBA').tobytes() # converte os dados para unsigned byte

        self.texId = glGenTextures(1) # cria um objeto textura
        glBindTexture(GL_TEXTURE_2D, self.texId) # torna o objeto ativo na unidade GL_TEXTURE0
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR) # filtragem (magnificação)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR) # filtragem (minificação)

        glTexImage2D(GL_TEXTURE_2D, # Tipo da textura. Normalmente GL_TEXTURE_2D
            0, # Nível de mipmap. Use 0 para a textura base (nível mais detalhado)
            GL_RGBA, # Formato interno da textura na GPU
            img.width, # largura da textura em pixels
            img.height, # altura da textura em pixels
            0, # Deve ser zero. Bordas diferentes estão obsoletas
            GL_RGBA, # Formato dos dados que estão sendo enviados (GL_RGB, GL_RGBA)
            GL_UNSIGNED_BYTE, # Tipo de dados do array (GL_UNSIGNED_BYTE, GL_FLOAT)
            imgData) # Ponteiro para os dados da imagem
        glGenerateMipmap(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, 0)
        pass
        

