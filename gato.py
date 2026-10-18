"""
Cada parte é o mesmo cubo unitário, desenhado com a matriz:

    junta = M_mae · T(pivo) · R(rotacao)      | passada para as partes filhas
    caixa = junta · T(centro) · S(tamanho)    | o que aparece na tela

  pivo   = onde fica a articulação, medido a partir da junta da parte-mãe
  centro = onde fica o meio da caixa
"""
import math
import glm

PX = 0.025  # 1 pixel = 2,5 cm

# 3 pelagens
PELAGENS = {
    "laranja": {"pelo": (0.93, 0.55, 0.20), "claro": (0.98, 0.88, 0.70),
                "escuro": (0.75, 0.38, 0.12), "olho": (0.15, 0.55, 0.25)},
    "cinza":   {"pelo": (0.55, 0.56, 0.60), "claro": (0.85, 0.85, 0.87),
                "escuro": (0.38, 0.39, 0.43), "olho": (0.85, 0.65, 0.10)},
    "frajola": {"pelo": (0.12, 0.12, 0.13), "claro": (0.95, 0.95, 0.95),
                "escuro": (0.06, 0.06, 0.07), "olho": (0.70, 0.80, 0.20)},
}

# ações com tempo de duração em segundos e o dinheiro que rendem
ACOES = {"comendo": (3.0, 10), "carinho": (2.5, 5), "brincando": (3.0, 8)}

class Parte:
    def __init__(self, tamanho, pivo, centro=(0, 0, 0), cor=(1, 1, 1)):
        self.tamanho = glm.vec3(tamanho)
        self.pivo = glm.vec3(pivo)
        self.centro = glm.vec3(centro)
        self.cor = cor
        self.rotacao = glm.vec3(0)  # ângulos em x, y, z (radianos)
        self.escala = glm.vec3(1)   # usada para fechar os olhos
        self.filhas = []

    def desenhar(self, shader, cubo, mae):
        junta = glm.translate(mae, self.pivo)
        junta = glm.rotate(junta, self.rotacao.y, glm.vec3(0, 1, 0))
        junta = glm.rotate(junta, self.rotacao.x, glm.vec3(1, 0, 0))
        junta = glm.rotate(junta, self.rotacao.z, glm.vec3(0, 0, 1))

        caixa = glm.translate(junta, self.centro)
        caixa = glm.scale(caixa, self.tamanho * self.escala)
        shader.material(self.cor)
        cubo.desenhar(shader, caixa)

        for filha in self.filhas:
            filha.desenhar(shader, cubo, junta)


class Gato:
    VELOCIDADE = 0.4  # metros por segundo

    def __init__(self, cubo, posicao=(0, 0, 0), pelagem="laranja"):
        self.cubo = cubo
        self.posicao = glm.vec3(posicao)
        self.direcao = 0.0       # ângulo em torno de Y (0 = olhando para +Z)
        self.estado = "parado" 
        self.destino = None
        self.tempo = 0.0
        self.tempo_acao = 0.0
        self.montar(pelagem)

    # ------------------------------------------------------------ montagem
    def montar(self, pelagem):
        c = PELAGENS[pelagem]
        self.pelagem = pelagem

        self.corpo = Parte((4, 6, 16), (0, 9, 0), cor=c["pelo"])

        self.cabeca = Parte((5, 4, 5), (0, 2, 7.5), (0, 1, 2), c["pelo"])
        focinho = Parte((3, 2, 1), (0, -0.5, 4.9), cor=c["claro"])
        nariz = Parte((1, 0.6, 0.3), (0, 0.6, 0.6), cor=(0.95, 0.55, 0.60))
        focinho.filhas = [nariz]
        orelha_e = Parte((1, 1, 2), (1.5, 3.5, 1.5), cor=c["escuro"])
        orelha_d = Parte((1, 1, 2), (-1.5, 3.5, 1.5), cor=c["escuro"])
        self.olho_e = Parte((1, 1, 0.2), (1.5, 1.6, 4.55), cor=c["olho"])
        self.olho_d = Parte((1, 1, 0.2), (-1.5, 1.6, 4.55), cor=c["olho"])
        self.cabeca.filhas = [focinho, orelha_e, orelha_d, self.olho_e, self.olho_d]

        # patas: articulação no quadril, caixa 3 px abaixo dela
        self.pata_fe = Parte((2, 6, 2), (1, -3, 6), (0, -3, 0), c["pelo"])
        self.pata_fd = Parte((2, 6, 2), (-1, -3, 6), (0, -3, 0), c["pelo"])
        self.pata_te = Parte((2, 6, 2), (1, -3, -6), (0, -3, 0), c["pelo"])
        self.pata_td = Parte((2, 6, 2), (-1, -3, -6), (0, -3, 0), c["pelo"])

        # rabo em dois pedaços: o segundo é filho do primeiro
        self.rabo1 = Parte((1, 1, 8), (0, 2.5, -7.5), (0, 0, -4), c["pelo"])
        self.rabo2 = Parte((1, 1, 8), (0, 0, -8), (0, 0, -4), c["pelo"])
        self.rabo1.filhas = [self.rabo2]

        self.corpo.filhas = [self.cabeca, self.pata_fe, self.pata_fd, self.pata_te, self.pata_td, self.rabo1]
        self.partes = [self.corpo, self.cabeca, self.pata_fe, self.pata_fd, self.pata_te, self.pata_td, self.rabo1, self.rabo2]

    def trocar_pelagem(self, pelagem):
        self.montar(pelagem)

    # ------------------------------------------------------------ comandos
    def ir_para(self, x, z):
        self.destino = glm.vec3(x, 0, z)
        self.estado = "andando"

    def sentar(self):
        # alterna entre sentado e parado
        self.destino = None
        self.estado = "parado" if self.estado == "sentado" else "sentado"

    def interagir(self, acao):
        # acao = 'comendo', 'carinho' ou 'brincando'
        if self.estado in ACOES:  # ainda ocupado com outra ação
            return 0
        self.destino = None
        self.estado = acao
        self.tempo_acao, dinheiro = ACOES[acao]
        return dinheiro

    # -------------------------------------------------------------- update
    def update(self, dt):
        self.tempo += dt

        if self.estado == "andando":
            caminho = self.destino - self.posicao
            distancia = glm.length(caminho)
            if distancia < 0.02:
                self.estado = "parado"
            else:
                self.direcao = math.atan2(caminho.x, caminho.z)
                passo = min(self.VELOCIDADE * dt, distancia)
                self.posicao += glm.normalize(caminho) * passo

        if self.estado in ACOES:
            self.tempo_acao -= dt
            if self.tempo_acao <= 0:
                self.estado = "parado"

        self.animar(dt)

    # ------------------------------------------------------------- animação
    def animar(self, dt):
        # cada estado diz para onde cada parte deve girar
        alvo = {p: glm.vec3(0) for p in self.partes}
        altura = 9.0           # altura do centro do corpo (px)
        olhos_fechados = False
        t = self.tempo

        # rabo levantado balançando
        alvo[self.rabo1] = glm.vec3(0.9, 0.25 * math.sin(t * 2), 0)
        alvo[self.rabo2] = glm.vec3(0.5, 0, 0)

        if self.estado == "andando":
            # patas em diagonal juntas
            onda = 0.6 * math.sin(t * 10)
            alvo[self.pata_fe].x = onda
            alvo[self.pata_td].x = onda
            alvo[self.pata_fd].x = -onda
            alvo[self.pata_te].x = -onda

        elif self.estado == "sentado":
            altura = 5.8
            alvo[self.corpo].x = -0.5  # levanta a frente do corpo
            alvo[self.cabeca].x = 0.5  # cabeça volta a olhar para frente
            alvo[self.pata_fe].x = alvo[self.pata_fd].x = 0.5   # patas da frente em pé
            alvo[self.pata_te].x = alvo[self.pata_td].x = -1.07 # patas de trás deitadas
            alvo[self.rabo1] = glm.vec3(0.35, 0.5, 0)
            alvo[self.rabo2] = glm.vec3(0, 0.9, 0)

        elif self.estado == "comendo":
            altura = 8.0
            alvo[self.corpo].x = 0.25                             # abaixa a frente
            alvo[self.cabeca].x = 0.8 + 0.08 * math.sin(t * 8)    # cabeça no pote
            alvo[self.pata_fe].x = alvo[self.pata_fd].x = -0.25   # patas retas de novo

        elif self.estado == "carinho":
            olhos_fechados = True
            alvo[self.cabeca].z = 0.25 * math.sin(t * 3)                # cabeça inclinando
            alvo[self.rabo1] = glm.vec3(1.1, 0.4 * math.sin(t * 9), 0)  # rabo abanando

        elif self.estado == "brincando":
            tapa = abs(math.sin(t * 6))
            altura = 8.0
            alvo[self.corpo].x = 0.15                             # abaixa a frente
            alvo[self.pata_fd].x = -0.15 - 1.2 * tapa             # pata dá tapinhas
            alvo[self.rabo1] = glm.vec3(0.6, 0.5 * math.sin(t * 6), 0)

        # cada parte se aproxima um pouco do alvo a cada frame (transição suave)
        suave = 1 - math.exp(-12 * dt)
        for parte in self.partes:
            parte.rotacao += (alvo[parte] - parte.rotacao) * suave
        self.corpo.pivo.y += (altura - self.corpo.pivo.y) * suave

        abertura = 0.25 if olhos_fechados else 1.0
        self.olho_e.escala.y = self.olho_d.escala.y = abertura

    # ------------------------------------------------------------- desenho
    def desenhar(self, shader):
        m = glm.translate(glm.mat4(1), self.posicao)
        m = glm.rotate(m, self.direcao, glm.vec3(0, 1, 0))
        m = glm.scale(m, glm.vec3(PX))
        self.corpo.desenhar(shader, self.cubo, m)