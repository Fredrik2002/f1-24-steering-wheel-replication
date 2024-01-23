import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.image as mpimg
from matplotlib.transforms import Affine2D
from matplotlib import transforms
import numpy as np
from math import cos, sin, pi
from parser2023 import Listener

class RotationApp:
    def __init__(self, master : tk.Tk):
        self.listener = Listener(port=20778)

        self.master = master
        self.master.title("Rotation d'éléments en 2D")

        self.fig = Figure(figsize=(5, 5), dpi=100)
        self.ax = self.fig.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.plot_elements()

        self.loop()

    def loop(self):
        self.running = True
        while self.running:
            a = self.listener.get()
            if a is not None:
                header, packet = a
                self.index = header.m_player_car_index
                if header.m_packet_id == 6:
                    self.packet_management(packet)
            self.master.update()
            self.master.update_idletasks()

    def packet_management(self, packet):
        angle = -packet.m_car_telemetry_data[self.index].m_steer*180
        gear = "N"
        self.rotate(angle, gear)



    def plot_elements(self):
        # Ajouter une image
        self.img_path = 'wheel.png' 
        self.img = mpimg.imread(self.img_path)
        self.img_plot = self.ax.imshow(self.img, extent=(-1, 1, -0.634, 0.634), origin='upper')

        #tr = transforms.Affine2D().rotate_deg(45)
        trans = Affine2D().translate(5,5)
        self.img_plot.set_transform(self.ax.transData + trans)

        # Ajouter du texte
        #self.text_plot = self.ax.text(0.5, 0.5, 'Mon texte', fontsize=12, ha='center', va='center', color='blue')
        self.ax.text(0,0.30,"N", fontsize=18, color='#88D7FF', ha='center', va='center')

        self.ax.set_xlim(-1,1)
        self.ax.set_ylim(-1,1)

    def rotate(self, angle_d, gear):
        
        angle_r = np.radians(angle_d)
        # Rotation du texte
        for text in self.ax.texts:
            text.set_position((0.3*cos(angle_r+pi/2), 0.3*sin(angle_r+pi/2)))
            text.set_rotation(angle_d)

        # Mise à jour de la transformation pour la rotation
        self.img_plot.remove()
        tr = transforms.Affine2D().translate(0,0).rotate(angle_r)
        self.img_plot = self.ax.imshow(self.img, transform=tr + self.ax.transData, extent=(-1, 1, -0.634, 0.634))
        self.canvas.draw()

def main():
    root = tk.Tk()
    app = RotationApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()