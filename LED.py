import matplotlib.patches as patches
from matplotlib.text import Text
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
    

class Custom_Text(Text):
    def __init__(self, x, y, label, size, c):
        super().__init__(x, y, label, fontsize=size, color=c, ha='center', va='center')
        self.init_angle = -arctan(x/y)+pi/2
        self.x = x
        self.y = y
        self.label = label
        self.color = c
        self.r = sqrt(x**2 + y**2)
