from panda3d.core import LineSegs 

from panda3d.core import Geom
from panda3d.core import GeomNode
from panda3d.core import GeomVertexFormat
from panda3d.core import GeomVertexData
from panda3d.core import GeomTriangles
from panda3d.core import GeomVertexWriter
from panda3d.core import GeomVertexReader
from panda3d.core import GeomVertexArrayFormat

from panda3d.core import Vec2
from panda3d.core import Vec3
from panda3d.core import Vec4


def linesegs_sample(x_segs, y_segs, wrap_x=False,
                    wrap_y=False, **columns):
    segs = LineSegs()
    for x in range(x_segs + 1):
        for y in range(y_segs + 1):
            x_e, y_e = x, y
            if wrap_x and x == x_segs:
                x_e = 0
            if wrap_y and y == y_segs:
                y_e = 0
            values = {
                name: f(
                    float(x_e) / float(x_segs),
                    float(y_e) / float(y_segs),
                )
                for name, (dtype, f) in columns.items()
            }
            if y == 0:
                segs.set_color(values['color'])
                segs.move_to(values['vertex'])
            else:
                segs.set_color(values['color'])
                segs.draw_to(values['vertex'])

    for y in range(y_segs + 1):
        for x in range(x_segs + 1):
            x_e, y_e = x, y
            if wrap_x and x == x_segs:
                x_e = 0
            if wrap_y and y == y_segs:
                y_e = 0
            values = {
                name: f(
                    float(x_e) / float(x_segs),
                    float(y_e) / float(y_segs),
                )
                for name, (dtype, f) in columns.items()
            }
            if x == 0:
                segs.set_color(values['color'])
                segs.move_to(values['vertex'])
            else:
                segs.set_color(values['color'])
                segs.draw_to(values['vertex'])

    return segs.create()


class GridSquareSampler:
    def __init__(self, comp_env):
        self.comp_env = comp_env

    def sample(self, segs, wrap_x=False, wrap_y=False, two_sided=False):
        self.comp_env.reset()

        x_segs, y_segs = segs
        array = GeomVertexArrayFormat()

        for column_name, column_func in self.comp_env.funcs.items():
            dtype = column_func.dtype_out
            if issubclass(dtype, Vec2):
                col_type = 2
            elif issubclass(dtype, Vec3):
                col_type = 3
            elif issubclass(dtype, Vec4):
                col_type = 4
            array.addColumn(
                column_name,
                col_type,
                Geom.NTFloat32,
                Geom.CPoint,
            )

        vformat = GeomVertexFormat()
        vformat.addArray(array)
        vformat = GeomVertexFormat.registerFormat(vformat)
        vdata = GeomVertexData("Data", vformat, Geom.UHDynamic)

        columns = {}
        for column_name in self.comp_env.outputs:
            columns[column_name] = GeomVertexWriter(vdata, column_name)

        geom = Geom(vdata)

        # Vertices
        x_vertices = x_segs + 1
        y_vertices = y_segs + 1
        if wrap_x:
            x_vertices -= 1
        if wrap_y:
            y_vertices -= 1

        for x in range(x_vertices):
            for y in range(y_vertices):
                x_norm = float(x) / float(x_segs)
                y_norm = float(y) / float(y_segs)

                self.comp_env.set_value('xy', Vec2(x_norm, y_norm))
                self.comp_env.compute()

                for column_name in self.comp_env.outputs:
                    writer = columns[column_name]
                    dtype = self.comp_env.funcs[column_name].dtype_out
                    data = self.comp_env.values[column_name]

                    if issubclass(dtype, Vec2):
                        writer.addData2f(data)
                    elif issubclass(dtype, Vec3):
                        writer.addData3f(data)
                    elif issubclass(dtype, Vec4):
                        writer.addData4f(data)

        # Triangles
        tris = GeomTriangles(Geom.UHStatic)
        for x in range(x_segs):
            for y in range(y_segs):
                # v1   v3
                #
                # v0   v2
                v_0 = x * y_vertices + y
                v_1 = x * y_vertices + y + 1
                v_2 = (x + 1) * y_vertices + y
                v_3 = (x + 1) * y_vertices + y + 1

                if wrap_x and x == x_segs - 1:
                    v_2 = y
                    v_3 = y + 1
                if wrap_y and y == y_segs - 1:
                    v_1 = x * y_vertices
                    v_3 = (x + 1) * y_vertices
                if wrap_x and x == x_segs - 1 and wrap_y and y == y_segs - 1:
                    v_3 = 0

                tris.addVertices(v_0, v_2, v_3)
                tris.addVertices(v_0, v_3, v_1)
                if two_sided:
                    tris.addVertices(v_0, v_3, v_2)
                    tris.addVertices(v_0, v_1, v_3)
        tris.closePrimitive()
        geom.addPrimitive(tris)

        node = GeomNode('geom_node')
        node.addGeom(geom)
        return node
