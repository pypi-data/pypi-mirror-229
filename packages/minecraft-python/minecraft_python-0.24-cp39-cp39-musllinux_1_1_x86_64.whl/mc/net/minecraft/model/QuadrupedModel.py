from mc.net.minecraft.model.BaseModel import BaseModel
from mc.net.minecraft.character.Cube import Cube

import math

class QuadrupedModel(BaseModel):

    def __init__(self):
        self.__head = Cube(0, 0)
        self.__head.addBox(-4.0, -4.0, -8.0, 8, 8, 8, 0.0)
        self.__head.setPos(0.0, 12.0, -6.0)
        self.__body = Cube(28, 8)
        self.__body.addBox(-5.0, -10.0, -7.0, 10, 16, 8, 0.0)
        self.__body.setPos(0.0, 11.0, 2.0)
        self.__leg1 = Cube(0, 16)
        self.__leg1.addBox(-2.0, 0.0, -2.0, 4, 6, 4, 0.0)
        self.__leg1.setPos(-3.0, 18.0, 7.0)
        self.__leg2 = Cube(0, 16)
        self.__leg2.addBox(-2.0, 0.0, -2.0, 4, 6, 4, 0.0)
        self.__leg2.setPos(3.0, 18.0, 7.0)
        self.__leg3 = Cube(0, 16)
        self.__leg3.addBox(-2.0, 0.0, -2.0, 4, 6, 4, 0.0)
        self.__leg3.setPos(-3.0, 18.0, -5.0)
        self.__leg4 = Cube(0, 16)
        self.__leg4.addBox(-2.0, 0.0, -2.0, 4, 6, 4, 0.0)
        self.__leg4.setPos(3.0, 18.0, -5.0)

    def render(self, x, y, z, xRot, yRot, zRot):
        self.__head.yRot = xRot / 57.29578
        self.__head.xRot = yRot / 57.29578
        self.__body.xRot = 1.5707963
        self.__leg1.xRot = math.cos(x * 0.6662) * 1.4 * y
        self.__leg2.xRot = math.cos(x * 0.6662 + math.pi) * 1.4 * y
        self.__leg3.xRot = math.cos(x * 0.6662 + math.pi) * 1.4 * y
        self.__leg4.xRot = math.cos(x * 0.6662) * 1.4 * y
        self.__head.render(zRot)
        self.__body.render(zRot)
        self.__leg1.render(zRot)
        self.__leg2.render(zRot)
        self.__leg3.render(zRot)
        self.__leg4.render(zRot)
