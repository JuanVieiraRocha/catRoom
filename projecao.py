import glfw
import OpenGL.GL as openGL
import OpenGL.GL.shaders as gls
import numpy as np

projMatrix = openGL.glFrustum(-1, 1, -1, 1, 1, 10)
gls.compileShader(projMatrix, openGL.GL_PROJECTION)