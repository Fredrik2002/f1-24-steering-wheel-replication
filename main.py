import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.image as mpimg
from matplotlib.transforms import Affine2D
from matplotlib import transforms
import numpy as np
import time
from parser2023 import Listener

class RotationApp:
    def __init__(self, master : tk.Tk):
        self.listener = Listener()

        self.master = master
        self.master.title("Rotation d'éléments en 2D")

        self.fig = Figure(figsize=(5, 5), dpi=100)
        self.ax = self.fig.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.angle_var = tk.DoubleVar()
        self.angle_var.set(0.0)

        angle_label = tk.Label(self.master, text="Angle de rotation:")
        angle_label.pack(side=tk.LEFT, padx=10)

        angle_entry = tk.Entry(self.master, textvariable=self.angle_var)
        angle_entry.pack(side=tk.LEFT)

        rotate_button = tk.Button(self.master, text="Tourner", command=self.rotate)
        rotate_button.pack(side=tk.LEFT, padx=10)

        self.plot_elements()

    def plot_elements(self):
        # Ajouter une image
        self.img_path = 'wheel.png'  # Remplacez 'votre_image.png' par le chemin de votre image
        self.img = mpimg.imread(self.img_path)
        self.img_plot = self.ax.imshow(self.img, extent=(-1, 1, -0.634, 0.634), origin='upper')

        #tr = transforms.Affine2D().rotate_deg(45)
        trans = Affine2D().translate(5,5)
        self.img_plot.set_transform(self.ax.transData + trans)

        # Ajouter du texte
        self.text_plot = self.ax.text(0.5, 0.5, 'Mon texte', fontsize=12, ha='center', va='center', color='blue')

        self.ax.set_xlim(-1,1)
        self.ax.set_ylim(-1,1)

    def rotate(self):
        angle_d = 0 # Convertir l'angle en radians
        monte = True
        
        while True:
            time.sleep(0.05)
            if monte:
                if angle_d == 180:
                    monte=False
                else:
                    angle_d += 1
            else:
                if angle_d ==-180:
                    monte=True
                else:
                    angle_d -=1
            angle_r = np.radians(angle_d)
            # Rotation du texte
            for text in self.ax.texts:
                text.set_rotation(angle_d)

            # Mise à jour de la transformation pour la rotation
            
            self.img_plot.remove()

            
            tr = transforms.Affine2D().translate(0,0).rotate(angle_r)
            self.img_plot = self.ax.imshow(self.img, transform=tr + self.ax.transData, extent=(-1, 1, -0.634, 0.634))
            print(angle_d)
            self.canvas.draw()
            self.master.update()
            self.master.update_idletasks()

def main():
    root = tk.Tk()
    app = RotationApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()