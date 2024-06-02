import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from ttkbootstrap import Menu
from matplotlib.figure import Figure
import matplotlib.image as mpimg
from matplotlib import transforms
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
from math import cos, sin
from parser2024 import Listener
from LED import *
from packet_management import *
import os
from os.path import exists
import sys


CENTRE_ROUGE = (0.195, 0.17)
CENTRE_VERT = (0.3, 0.17)

function_dict = {
    2:packet_lap_data_management,
    5:packet_car_setup_management,
    6:packet_telemetry_management,
    7:packet_car_status_management
}

script_directory = os.path.dirname(os.path.abspath(sys.argv[0]))
if exists(script_directory+"/settings.txt"):
    try:
        with open(script_directory+"/settings.txt", "r") as f:
            dictionnary_settings = json.load(f)
    except Exception as e:
        print(e)
        choice = input("Unable to read settings.txt, do you want to recreate settings.txt and start the program ? [Y|n]")
        if choice in ["n", "N"]:
            print("Aborting to recreate settings.txt, try to fix it by yourself, or simply delete settings.txt")
            exit(-1)
        else:
            print("Listening on default port 20777 and recreating settings.txt")
            dictionnary_settings = {"port": "20777", "redirect_active": 0, "ip_adress": "127.0.0.1", "redirect_port": "20778"}
            with open(script_directory+"/settings.txt", "w") as f:
                json.dump(dictionnary_settings, f)
else: #If settings.txt has been deleted, we recreate it
    dictionnary_settings = {"port":20777}
    with open(script_directory+"/settings.txt", "w") as f:
        json.dump(dictionnary_settings, f)


class RotationApp:
    def __init__(self, master : tk.Tk):
        self.PORT = dictionnary_settings['port']
        self.listener = Listener(port=int(self.PORT))

        self.master = master
        self.master.title("SF-23 Steering Wheel Replication")

        self.master.geometry("600x600")
        self.master.minsize(400,400) 
        self.master.protocol("WM_DELETE_WINDOW", self.close_window)
        self.master.bind("<Configure>", self.on_resize)

        self.fig = Figure(figsize=(12,7), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.axis('off')

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        menubar = Menu(self.master)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="PORT Selection", command=lambda : port_selection(dictionnary_settings, self))
        filemenu.add_command(label="UDP Redirect", command=lambda : UDP_Redirect(dictionnary_settings, self))
        menubar.add_cascade(label="Settings", menu=filemenu)
        self.master.config(menu=menubar)

        self.font_scale = 1

        self.list_text_elements = []

        self.angle = 0 
        self.rpm = 0  
        self.speed = 0  
        self.gear = 0 
        self.last_lap_time = 0
        self.ers_pourcentage = 100
        self.ers_mode = 1
        self.brake_bias = "55%"
        self.tyres_temp = [100]*4
        self.lap_num = 0
        self.sc_delta = 0
        self.revLightBitValue = 0xffff
        self.vehicleFiaFlag = 0
        self.list_cercles : list[LED] = []
        self.side_leds : list[LED] = []

        self.plot_elements()
        self.rotate()

        self.loop()

    def reset(self):
        self.angle = 0 
        self.rpm = 0  
        self.speed = 0  
        self.gear = 0 
        self.last_lap_time = 0
        self.ers_pourcentage = 100
        self.ers_mode = 1
        self.brake_bias = "55%"
        self.tyres_temp = [100]*4
        self.lap_num = 0
        self.sc_delta = 0
        self.revLightBitValue = 0xffff
        self.vehicleFiaFlag = 0

        self.rotate()

    def on_resize(self, e):
        self.font_scale = 0.0015*min(e.width, e.height)+0.1
        self.rotate()
        
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
                if header.m_packet_id in [2,5,6,7]:
                    function_dict[header.m_packet_id](self, packet)
                    
            self.master.update()
            self.master.update_idletasks()
        
        
    def rotate(self):
        update_labels(self)
        angle_r = np.radians(self.angle)

        # Steering wheel
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

        #REV Lights
        
        for circle in self.list_cercles:
            if not self.revLightBitValue&1:
                circle.set_visible(False)
            else:
                r, a = circle.r, circle.init_angle
                circle.set_center((r*cos(angle_r+a), r*sin(angle_r+a)))
                circle.set_visible(True)
            self.revLightBitValue = self.revLightBitValue >> 1
                

        #Side LEDs
        
        for i, circle in enumerate(self.side_leds):
            if self.vehicleFiaFlag==0:
                circle.set_visible(False)
            else:
                r, a = circle.r, circle.init_angle
                circle.set_visible(True)
                circle.set_center((r*cos(angle_r+a), r*sin(angle_r+a)))
                circle.set_color(color_dict[self.vehicleFiaFlag])


        #Delta
        if self.sc_delta>0:
            self.list_text_elements[7].color = "green"
            self.list_text_elements[7].label ="+"+str(abs(self.sc_delta))
        elif self.sc_delta == 0:
            self.list_text_elements[7].color = "#88D7FF"
            self.list_text_elements[7].label ="+"+str(abs(self.sc_delta))
        else:
            self.list_text_elements[7].color = "red"

        #Dashboard
        for text in self.list_text_elements:
            theta, r = text.init_angle, text.r
            text.set_fontsize(text.size*self.font_scale)
            text.set_text(text.label)
            text.set_position((r*cos(angle_r+theta), r*sin(angle_r+theta)))
            text.set_rotation(self.angle)
            text.set_color(text.color)

        self.canvas.draw()

    def plot_elements(self):
        # Ajouter une image
        self.img_path = script_directory+'/wheel.png' 
        self.img = mpimg.imread(self.img_path)
        self.img_plot = self.ax.imshow(self.img, extent=(-1, 1, -0.634, 0.634), origin='upper')

        self.list_text_elements.append(Custom_Text(0,0.30,"N", 18, '#88D7FF')) # Gear
        self.list_text_elements.append(Custom_Text(-0.26,0.35,"250",12, '#88D7FF')) # Speed
        self.list_text_elements.append(Custom_Text(-0.28,0.27,"44", 12, '#88D7FF')) # Lap number
        self.list_text_elements.append(Custom_Text(0,0.45,"10800", 12, 'red')) # RPM
        self.list_text_elements.append(Custom_Text(-0.22,0.45,"1:30:530", 8, '#88FFA3')) # Previous lap time
        self.list_text_elements.append(Custom_Text(0.25,0.35,"50%", 12, '#88D7FF')) # Brake bias
        self.list_text_elements.append(Custom_Text(0.25,0.27,"1", 12, '#88D7FF')) # ERS Mode
        self.list_text_elements.append(Custom_Text(0.23,0.45,0, 12, '#88D7FF')) # Safety Car Delta

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
            circle = LED(*LED_positions[i], color)
            self.list_cercles.append(circle)
            self.ax.add_patch(circle)
        for i in range(6):
            circle = LED(*side_leds_positions[i], "yellow")
            self.side_leds.append(circle)
            self.ax.add_patch(circle)


        self.ax.set_xlim(-1,1)
        self.ax.set_ylim(-1,1)

    

def main():
    root = tk.Tk()
    app = RotationApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()