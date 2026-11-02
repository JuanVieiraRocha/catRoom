from OpenGL.GL import *
import pywavefront
# import pywavefront.visualization


# class loadObj:
#     def __init__(self, obj_path, scale=(1, 1, 1), position=(0, 0, 0), rotation=(0, 0, 0)):
#         self.obj_path = obj_path
#         self.scale = scale
#         self.position = position
#         self.rotation = rotation

#         self.obj = pywavefront.Wavefront(self.obj_path, collect_faces=True)

#     def draw(self):
#         glPushMatrix()
#         glTranslatef(*self.position)
#         glScale(*self.scale)
#         glRotatef(self.rotation[0], 1, 0, 0)
#         glRotatef(self.rotation[1], 0, 1, 0,)
#         glRotatef(self.rotation[2], 0, 0, 1,)

#         pywavefront.visualization.draw(self.obj)

#         glPopMatrix()


## Função utilizando glfw
import numpy as np
import glm

def load_obj(filename):
    temp_vertices = []
    temp_uvs = []
    temp_normals = []

    final_vertices = []
    final_uvs = []
    final_normals = []

    with open(filename, 'r') as file:
        for line in file:
            if line.startswith('#'):
                continue
            parts = line.split()
            if not parts:
                continue

            # Posições dos Vértices
            if parts[0] == 'v':
                temp_vertices.append(glm.vec3(float(parts[1]), float(parts[2]), float(parts[3])))
            # Coordenadas UV
            elif parts[0] == 'vt':
                temp_uvs.append(glm.vec2(float(parts[1]), float(parts[2])))
            # Vetores Normais
            elif parts[0] == 'vn':
                temp_normals.append(glm.vec3(float(parts[1]), float(parts[2]), float(parts[3])))
            # Faces (triângulos no formato v/vt/vn)
            elif parts[0] == 'f':
                for vertex_data in parts[1:4]:
                    indices = vertex_data.split('/')
                    
                    v_idx = int(indices[0]) - 1
                    uv_idx = int(indices[1]) - 1 if len(indices) > 1 and indices[1] != '' else None
                    n_idx = int(indices[2]) - 1 if len(indices) > 2 and indices[2] != '' else None

                    # Vértice
                    v = temp_vertices[v_idx]
                    final_vertices.extend([v.x, v.y, v.z])

                    # UV
                    if uv_idx is not None and temp_uvs:
                        uv = temp_uvs[uv_idx]
                        final_uvs.extend([uv.x, uv.y])

                    # Normal
                    if n_idx is not None and temp_normals:
                        n = temp_normals[n_idx]
                        final_normals.extend([n.x, n.y, n.z])

    return (
        np.array(final_vertices, dtype=np.float32),
        np.array(final_uvs, dtype=np.float32),
        np.array(final_normals, dtype=np.float32)
    )