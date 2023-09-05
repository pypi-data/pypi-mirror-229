# cython: language_level=3

from libc.math cimport sin, cos, pi

from mc.net.minecraft.renderer.Tesselator cimport Tesselator
from mc.net.minecraft.level.tile.Tile cimport Tile

cdef class Flower(Tile):

    def __init__(self, tiles, int id_, int tex):
        Tile.__init__(self, tiles, id_, tex)
        self.tex = tex
        self._setTicking(True)
        cdef float f = 0.2
        self._setShape(0.5 - f, 0.0, 0.5 - f, f + 0.5, f * 2.0, f + 0.5)

    cpdef void tick(self, level, int x, int y, int z, random) except *:
        cdef int below = level.getTile(x, y - 1, z)
        if not level.isLit(x, y, z) or (below != self.tiles.dirt.id and below != self.tiles.grass.id):
            level.setTile(x, y, z, 0)

    cpdef bint render(self, Tesselator t, level, int layer, int x, int y, int z) except *:
        cdef float b = level.getBrightness(x, y, z)
        t.colorFloat(b, b, b)
        self.__renderFlower(t, x, y, z)
        return True

    cdef void __renderFlower(self, Tesselator t, float x, float y, float z) except *:
        cdef int tex, xt, yt, rots, r
        cdef float u0, u1, v0, v1, xa, za, x0, x1, y0, y1, z0, z1

        tex = self._getTexture(15)
        if not self.isNormalTile:
            xt = tex % 16 << 4
            yt = tex // 16 << 4
            u0 = xt / 256.0
            u1 = (xt + 15.99) / 256.0
            v0 = yt / 256.0
            v1 = (yt + 15.99) / 256.0
        else:
            xt = tex % 16
            yt = (xt << 4) + tex // 16 << 4
            u0 = 0.0
            u1 = 1.0
            v0 = yt / 4096.0
            v1 = (yt + 15.99) / 4096.0

        rots = 2
        for r in range(rots):
            xa = sin(r * pi / rots + 0.7854) * 0.5
            za = cos(r * pi / rots + 0.7854) * 0.5
            x0 = x + 0.5 - xa
            x1 = x + 0.5 + xa
            y0 = y + 0.0
            y1 = y + 1.0
            z0 = z + 0.5 - za
            z1 = z + 0.5 + za

            t.vertexUV(x0, y1, z0, u1, v0)
            t.vertexUV(x1, y1, z1, u0, v0)
            t.vertexUV(x1, y, z1, u0, v1)
            t.vertexUV(x0, y, z0, u1, v1)

            t.vertexUV(x1, y1, z1, u1, v0)
            t.vertexUV(x0, y1, z0, u0, v0)
            t.vertexUV(x0, y, z0, u0, v1)
            t.vertexUV(x1, y, z1, u1, v1)

    def getTileAABB(self, int x, int y, int z):
        return None

    cpdef bint blocksLight(self):
        return False

    cpdef bint isSolid(self):
        return False

    def renderGuiTile(self, Tesselator t):
        t.normal(0.0, 1.0, 0.0)
        t.begin()
        self.__renderFlower(t, 0.0, 0.4, -0.3)
        t.end()

    cdef bint isOpaque(self):
        return False
