import criandoObjetos
import setUp

def init():  # Define as propriedades iniciadas
    criandoObjetos.corDeFundo()
    setUp.inicializarJanela()

def render():
    criandoObjetos.renderizacao()

init()