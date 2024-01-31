import matplotlib.patches as patches
from matplotlib.text import Text
from numpy import arctan
from math import pi, sqrt

RADIUS = 0.015

LED_positions = [(-0.302, 0.558), #0.0435
                 (-0.2565, 0.56),
                 (-0.213, 0.56),
                 (-0.1695, 0.56),
                 (-0.126, 0.56),

                 (-0.0825, 0.562),
                 (-0.039, 0.562),
                 (0.0045, 0.562),
                 (0.048, 0.562),
                 (0.0915, 0.562),

                 (0.1344, 0.563),
                 (0.178, 0.562),
                 (0.2213, 0.56),
                 (0.2651, 0.56),
                 (0.3083, 0.557)]

side_leds_positions = [
    (-0.4, 0.50),
    (-0.4, 0.455),
    (-0.4, 0.41),

    (0.4, 0.50),
    (0.4, 0.455),
    (0.4, 0.41)
]

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
        self.size = size
        self.r = sqrt(x**2 + y**2)
