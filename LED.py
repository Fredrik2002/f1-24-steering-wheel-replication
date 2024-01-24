import matplotlib.patches as patches
from numpy import arctan
from math import pi, sqrt

RADIUS = 0.015

class LED(patches.Circle):
    def __init__(self, x, y, color) -> None:
        super().__init__((x, y), RADIUS, facecolor=color)
        self.init_angle = -arctan(x/y)+pi/2
        self.color = color
        self.radius = RADIUS
        self.x = x
        self.y = y
        self.r = sqrt(x**2 + y**2)
        self.visible = True

    def __str__(self):
        return self.color
    
    def __repr__(self):
        return self.color