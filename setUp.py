import glfw

def inicializarJanela():
    glfw.init()
    window = glfw.create_window(500, 500, 'catRoom - Um Cozy gato de Jogos', None, None)
    glfw.make_context_current(window)
    while not glfw.window_should_close(window):
        glfw.poll_events()
        glfw.swap_buffers(window)
    glfw.terminate()