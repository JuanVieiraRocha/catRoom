from OpenGL.GL import *
import pywavefront
import pywavefront.visualization


class loadObj:
    def __init__(self, obj_path, scale=(1, 1, 1), position=(0, 0, 0), rotation=(0, 0, 0)):
        self.obj_path = obj_path
        self.scale = scale
        self.position = position
        self.rotation = rotation

        self.obj = pywavefront.Wavefront(self.obj_path, collect_faces=True)

    def draw(self):
        glPushMatrix()
        glTranslatef(*self.position)
        glScale(*self.scale)
        glRotatef(self.rotation[0], 1, 0, 0)
        glRotatef(self.rotation[1], 0, 1, 0,)
        glRotatef(self.rotation[2], 0, 0, 1,)

        pywavefront.visualization.draw(self.obj)

        glPopMatrix()
