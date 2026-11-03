from OpenGL.GL import *


class loadObj:
    """Carrega e desenha um arquivo OBJ com OpenGL imediato."""

    def __init__(self, obj_path, scale=(1, 1, 1), position=(0, 0, 0), rotation=(0, 0, 0)):
        self.obj_path = obj_path
        self.scale = scale
        self.position = position
        self.rotation = rotation
        self.vertices = []
        self.texture_coordinates = []
        self.normals = []
        self.faces = []
        self._carregar()

    @staticmethod
    def _indice(valor, quantidade):
        indice = int(valor)
        return indice - 1 if indice > 0 else quantidade + indice

    def _carregar(self):
        with open(self.obj_path, encoding="utf-8") as arquivo:
            for linha in arquivo:
                partes = linha.split()
                if not partes or partes[0].startswith('#'):
                    continue

                if partes[0] == "v":
                    self.vertices.append(tuple(map(float, partes[1:4])))
                elif partes[0] == "vt":
                    self.texture_coordinates.append(tuple(map(float, partes[1:3])))
                elif partes[0] == "vn":
                    self.normals.append(tuple(map(float, partes[1:4])))
                elif partes[0] == "f":
                    face = []
                    for referencia in partes[1:]:
                        indices = referencia.split("/")
                        face.append(tuple(
                            None if indice == "" else indice
                            for indice in indices
                        ))
                    self.faces.append(face)

    def draw(self):
        glPushMatrix()
        glTranslatef(*self.position)
        glScalef(*self.scale)
        glRotatef(self.rotation[0], 1, 0, 0)
        glRotatef(self.rotation[1], 0, 1, 0)
        glRotatef(self.rotation[2], 0, 0, 1)

        glBegin(GL_TRIANGLES)
        for face in self.faces:
            # Triangulacao em leque para faces triangulares, quadriculas e n-gonos.
            for posicao in range(1, len(face) - 1):
                for vertice_referencia in (face[0], face[posicao], face[posicao + 1]):
                    indice_vertice, indice_uv, indice_normal = vertice_referencia

                    if indice_normal is not None and indice_normal != "None":
                        normal = self.normals[self._indice(indice_normal, len(self.normals))]
                        glNormal3fv(normal)
                    if indice_uv is not None and indice_uv != "None":
                        uv = self.texture_coordinates[self._indice(indice_uv, len(self.texture_coordinates))]
                        glTexCoord2fv(uv)

                    vertice = self.vertices[self._indice(indice_vertice, len(self.vertices))]
                    glVertex3fv(vertice)
        glEnd()

        glPopMatrix()


## Função utilizando glfw
import numpy as np


class Estrutura:
    def __init__(self, obj_path, scale=(1, 1, 1), position=(0, 0, 0), rotation=(0, 0, 0)):
        self.obj_path = obj_path
        self.scale = scale
        self.position = position
        self.rotation = rotation
        pass


def load_obj(filename):
    temp_vertices = []
    temp_uvs = []
    temp_normals = []

    final_vertices = []
    final_uvs = []
    final_normals = []

    def resolve_indice(valor, quantidade):
        indice = int(valor)
        return indice - 1 if indice > 0 else quantidade + indice

    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            parts = line.split()
            if not parts or parts[0].startswith('#'):
                continue

            if parts[0] == 'v':
                temp_vertices.append(tuple(map(float, parts[1:4])))
            elif parts[0] == 'vt':
                temp_uvs.append(tuple(map(float, parts[1:3])))
            elif parts[0] == 'vn':
                temp_normals.append(tuple(map(float, parts[1:4])))
            elif parts[0] == 'f':
                face = []
                for vertex_data in parts[1:]:
                    indices = vertex_data.split('/')
                    face.append(tuple(None if item == '' else item for item in indices))

                # OBJ também permite quads/polígonos; usa triangulação em leque.
                for posicao in range(1, len(face) - 1):
                    for vertex_indices in (face[0], face[posicao], face[posicao + 1]):
                        v_idx = resolve_indice(vertex_indices[0], len(temp_vertices))
                        final_vertices.extend(temp_vertices[v_idx])

                        if len(vertex_indices) > 1 and vertex_indices[1] is not None:
                            uv_idx = resolve_indice(vertex_indices[1], len(temp_uvs))
                            final_uvs.extend(temp_uvs[uv_idx])

                        if len(vertex_indices) > 2 and vertex_indices[2] is not None:
                            n_idx = resolve_indice(vertex_indices[2], len(temp_normals))
                            final_normals.extend(temp_normals[n_idx])

    return (
        np.array(final_vertices, dtype=np.float32).reshape(-1, 3),
        np.array(final_uvs, dtype=np.float32).reshape(-1, 2),
        np.array(final_normals, dtype=np.float32).reshape(-1, 3)
    )