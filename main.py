import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.image as mpimg
from matplotlib import transforms
import matplotlib.patches as patches
import numpy as np
from math import cos, sin, pi
from parser2023 import Listener

#gear, speed, lap_number, rpm, lap_time, SOC
angle_offset = [pi/2, 
                36.6*pi/180+pi/2,
                46*pi/180+pi/2,
                pi/2,
                26.05*pi/180+pi/2,
                -35.53*pi/180 + pi/2,
                -42.8*pi/180 + pi/2  ]
rayon_offset = [0.3,0.436, 0.389, 0.45, 0.5, 0.43, 0.368]

CENTRE_ROUGE = (0.195, 0.17)
CENTRE_VERT = (0.3, 0.17)

def conversion(millis):
    seconds, millis = millis // 1000, millis%1000
    minutes, seconds = seconds // 60, seconds%60
    if (minutes!=0 or seconds!=0 or millis!=0) and (minutes>=0 and seconds<10):
        seconds = "0"+str(seconds)

    if millis//10 == 0:
        millis="00"+str(millis)
    elif millis//100 == 0:
        millis="0"+str(millis)
    
    if minutes != 0:
        return f"{minutes}:{seconds}.{millis}"
    else:
        return f"{seconds}.{millis}"

class RotationApp:
    def __init__(self, master : tk.Tk):
        self.listener = Listener(port=20778)

        self.master = master
        self.master.title("Rotation d'éléments en 2D")

        self.master.geometry("1080x600") 
        #self.master.resizable(width=False, height=False)

        self.fig = Figure(figsize=(10, 5), dpi=100)
        self.ax = self.fig.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.list_text_elements = []

        self.angle, self.rpm, self.speed, self.gear, self.last_lap_time = 0,0,0,0, 0
        self.ers_pourcentage = 100
        self.ers_mode = 1
        self.brake_bias = "50%"
        self.labels = [self.angle, self.gear, self.speed, self.rpm, self.last_lap_time]

        self.plot_elements()

        self.loop()

    def loop(self):
        self.running = True
        while self.running:
            a = self.listener.get()
            if a is not None:
                header, packet = a
                self.index = header.m_player_car_index
                match header.m_packet_id:
                    case 2:
                        self.packet_lap_data_management(packet)
                    case 5:
                        self.packet_car_setup_management(packet)
                    case 6:
                        self.packet_telemetry_management(packet)
                    case 7:
                        self.packet_car_status_management(packet)
            self.master.update()
            self.master.update_idletasks()

    def packet_lap_data_management(self, packet):
        self.last_lap_time = packet.m_lap_data[self.index].m_last_lap_time_in_ms

    def packet_car_setup_management(self, packet):
        self.brake_bias = packet.m_car_setups[self.index].m_brake_bias
    
    def packet_telemetry_management(self, packet):
        self.angle = -packet.m_car_telemetry_data[self.index].m_steer*180
        self.gear = packet.m_car_telemetry_data[self.index].m_gear
        self.speed = packet.m_car_telemetry_data[self.index].m_speed
        self.rpm = packet.m_car_telemetry_data[self.index].m_engine_rpm
        self.revLightPercent = packet.m_car_telemetry_data[self.index].m_rev_lights_percent
        self.revLightBitValue = packet.m_car_telemetry_data[self.index].m_rev_lights_bit_value
        if self.gear == 0:
            self.gear = "N"
        elif self.gear == -1:
            self.gear = "R"
        self.labels = [self.gear, self.speed, "44", self.rpm, conversion(self.last_lap_time), self.brake_bias, self.ers_mode]
        self.rotate()

    def packet_car_status_management(self, packet):
        self.ers_pourcentage = round(packet.m_car_status_data[self.index].m_ers_store_energy/40_000)
        self.ers_mode = packet.m_car_status_data[self.index].m_ers_deploy_mode
    
    def rotate(self):
        angle_r = np.radians(self.angle)
        for text, label, theta, r in zip(self.list_text_elements, self.labels, angle_offset, rayon_offset):
            text.set_text(label)
            text.set_position((r*cos(angle_r+theta), r*sin(angle_r+theta)))
            text.set_rotation(self.angle)

        # Mise à jour de la transformation pour la rotation
        self.img_plot.remove()
        tr = transforms.Affine2D().rotate(angle_r)
        self.img_plot = self.ax.imshow(self.img, transform=tr + self.ax.transData, extent=(-1, 1, -0.634, 0.634))

        trans_rouge = transforms.Affine2D().rotate_deg(self.angle)
        trans_vert = transforms.Affine2D().rotate_deg(self.angle)

        if self.ers_pourcentage<=35:
            self.rectangle_vert.set_width(0)
            self.rectangle_rouge.set_width(self.ers_pourcentage*0.21/35)
        else:
            self.rectangle_vert.set_width((self.ers_pourcentage-35)*0.39/65)
            self.rectangle_rouge.set_width(0.21)
        print(self.ers_pourcentage)
        self.rectangle_rouge.set_transform(trans_rouge + self.ax.transData)
        self.rectangle_vert.set_transform(trans_vert + self.ax.transData)

        self.canvas.draw()

    def plot_elements(self):
        # Ajouter une image
        self.img_path = 'wheel.png' 
        self.img = mpimg.imread(self.img_path)
        self.img_plot = self.ax.imshow(self.img, extent=(-1, 1, -0.634, 0.634), origin='upper')

        self.list_text_elements.append(self.ax.text(0,0.30,"N", fontsize=18, color='#88D7FF', ha='center', va='center'))
        self.list_text_elements.append(self.ax.text(-0.26,0.35,"250", fontsize=12, color='#88D7FF', ha='center', va='center'))
        self.list_text_elements.append(self.ax.text(-0.28,0.27,"44", fontsize=12, color='#88D7FF', ha='center', va='center'))
        self.list_text_elements.append(self.ax.text(0,0.45,"10800", fontsize=12, color='red', ha='center', va='center'))
        self.list_text_elements.append(self.ax.text(-0.22,0.45,"1:30:530", fontsize=8, color='#88FFA3', ha='center', va='center'))
        self.list_text_elements.append(self.ax.text(0.25,0.35,"50%", fontsize=12, color='#88D7FF', ha='center', va='center'))
        self.list_text_elements.append(self.ax.text(0.25,0.27,"1", fontsize=12, color='#88D7FF', ha='center', va='center'))

        self.rectangle_rouge = patches.Rectangle((-0.3, 0.15), 0.21, 0.04, linewidth=0, facecolor='red')
        self.rectangle_vert = patches.Rectangle((-0.09, 0.15), 0.39, 0.04, linewidth=0, facecolor='green')
        self.ax.add_patch(self.rectangle_rouge)
        self.ax.add_patch(self.rectangle_vert)


        self.ax.set_xlim(-1,1)
        self.ax.set_ylim(-1,1)

    

def main():
    root = tk.Tk()
    app = RotationApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()