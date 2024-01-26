import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.image as mpimg
from matplotlib import transforms
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
from math import cos, sin, pi
from numpy import arctan
from parser2023 import Listener
from LED import *
from packet_management import *


CENTRE_ROUGE = (0.195, 0.17)
CENTRE_VERT = (0.3, 0.17)



class RotationApp:
    def __init__(self, master : tk.Tk):
        self.listener = Listener(port=20777)

        self.master = master
        self.master.title("Rotation d'éléments en 2D")

        self.master.geometry("1080x600") 
        #self.master.resizable(width=False, height=False)
        self.master.protocol("WM_DELETE_WINDOW", self.close_window)

        self.fig = Figure(figsize=(10, 5), dpi=100)
        self.ax = self.fig.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.list_text_elements = []

        self.angle = 0 
        self.rpm = 0  
        self.speed = 0  
        self.gear = 0 
        self.last_lap_time = 0
        self.ers_pourcentage = 100
        self.ers_mode = 1
        self.brake_bias = "50%"
        self.tyres_temp = [100]*4
        self.lap_num = 0
        self.sc_delta = 0
        self.revLightBitValue = "0"
        self.list_cercles : list[LED] = []

        self.plot_elements()

        self.loop()

    def close_window(self):
        plt.close()
        self.master.destroy()
        self.running = False

    def loop(self):
        self.running = True
        while self.running:
            a = self.listener.get()
            if a is not None:
                header, packet = a
                self.index = header.m_player_car_index
                match header.m_packet_id:
                    case 2:
                        packet_lap_data_management(self, packet)
                    case 5:
                        packet_car_setup_management(self, packet)
                    case 6:
                        packet_telemetry_management(self, packet)
                    case 7:
                        packet_car_status_management(self, packet)
            self.master.update()
            self.master.update_idletasks()
        quit()
        
        
    def rotate(self):
        angle_r = np.radians(self.angle)
        for text in self.list_text_elements:
            theta, r = text.init_angle, text.r
            text.set_text(text.label)
            text.set_position((r*cos(angle_r+theta), r*sin(angle_r+theta)))
            text.set_rotation(self.angle)

        # Mise à jour de la transformation pour la rotation
        self.img_plot.remove()
        tr = transforms.Affine2D().rotate(angle_r)
        self.img_plot = self.ax.imshow(self.img, transform=tr + self.ax.transData, extent=(-1, 1, -0.634, 0.634))

        trans_rouge = transforms.Affine2D().rotate_deg(self.angle)
        trans_vert = transforms.Affine2D().rotate_deg(self.angle)

        #ERS Bar
        if self.ers_pourcentage<=35:
            self.rectangle_vert.set_width(0)
            self.rectangle_rouge.set_width(self.ers_pourcentage*0.21/35)
        else:
            self.rectangle_vert.set_width((self.ers_pourcentage-35)*0.39/65)
            self.rectangle_rouge.set_width(0.21)
        self.rectangle_rouge.set_transform(trans_rouge + self.ax.transData)
        self.rectangle_vert.set_transform(trans_vert + self.ax.transData)
        l = len(self.revLightBitValue)

        #REV Lights
        for i, circle in enumerate(self.list_cercles):
            if i+2>=l or self.revLightBitValue[i+2]==0:
                circle.set_visible(False)
            else:
                r, a = circle.r, circle.init_angle
                circle.set_center((r*cos(angle_r+a), r*sin(angle_r+a)))
                circle.set_visible(True)

        #Delta
        if self.sc_delta<0:
            self.list_text_elements[7].color = "green"
        elif self.sc_delta == 0:
            self.list_text_elements[7].color = "#88D7FF"
            self.sc_delta ="+"+str(self.sc_delta)
        else:
            self.list_text_elements[7].color = "red"
            self.sc_delta ="+"+str(self.sc_delta)

        self.canvas.draw()

    def plot_elements(self):
        # Ajouter une image
        self.img_path = 'wheel.png' 
        self.img = mpimg.imread(self.img_path)
        self.img_plot = self.ax.imshow(self.img, extent=(-1, 1, -0.634, 0.634), origin='upper')

        self.list_text_elements.append(Custom_Text(0,0.30,"N", 18, '#88D7FF')) # Gear
        self.list_text_elements.append(Custom_Text(-0.26,0.35,"250",12, '#88D7FF')) # Speed
        self.list_text_elements.append(Custom_Text(-0.28,0.27,"44", 12, '#88D7FF')) # Lap number
        self.list_text_elements.append(Custom_Text(0,0.45,"10800", 12, 'red')) # RPM
        self.list_text_elements.append(Custom_Text(-0.22,0.45,"1:30:530", 8, '#88FFA3')) # Previous lap time
        self.list_text_elements.append(Custom_Text(0.25,0.35,"50%", 12, '#88D7FF')) # Brake bias
        self.list_text_elements.append(Custom_Text(0.25,0.27,"1", 12, '#88D7FF')) # ERS Mode
        self.list_text_elements.append(Custom_Text(0.23,0.45,"+0.0", 12, '#88D7FF')) # Safety Car Delta

        self.list_text_elements.append(Custom_Text(-0.13,0.27,"100",10, 'red')) # RL
        self.list_text_elements.append(Custom_Text(0.11,0.27,"100",10, 'red')) # RR
        self.list_text_elements.append(Custom_Text(-0.13,0.35,"100",10, 'red')) # FL
        self.list_text_elements.append(Custom_Text(0.11,0.35,"100",10, 'red')) # FR


        for element in self.list_text_elements:
            self.ax.add_artist(element)

        self.rectangle_rouge = patches.Rectangle((-0.3, 0.15), 0.21, 0.04, linewidth=0, facecolor='red')
        self.rectangle_vert = patches.Rectangle((-0.09, 0.15), 0.39, 0.04, linewidth=0, facecolor='green')
        self.ax.add_patch(self.rectangle_rouge)
        self.ax.add_patch(self.rectangle_vert)

        for i in range(15):
            if i<=4: color = "green"
            elif i<=9: color = "red"
            else: color = "blue"
            circle = LED(-0.30+i*0.0435, 0.56, color)
            self.list_cercles.append(circle)
            self.ax.add_patch(circle)


        self.ax.set_xlim(-1,1)
        self.ax.set_ylim(-1,1)

    

def main():
    root = tk.Tk()
    app = RotationApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()