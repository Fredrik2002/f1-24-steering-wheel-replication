import json
from ttkbootstrap import Toplevel, Entry, Label, IntVar, Checkbutton
from tkinter import Message, Button, LEFT
import os
import sys

script_directory = os.path.dirname(os.path.abspath(sys.argv[0]))

color_dict = {
    0:"#13FE13",
    1:"#13FE13",
    2:"blue",
    3:"yellow"
}

def packet_lap_data_management(self, packet):
        self.last_lap_time = packet.m_lap_data[self.index].m_last_lap_time_in_ms
        self.lap_num = packet.m_lap_data[self.index].m_current_lap_num
        self.sc_delta = round(packet.m_lap_data[self.index].m_safety_car_delta, 3)

        self.rotate()

def packet_car_setup_management(self, packet):
    self.brake_bias = packet.m_car_setups[self.index].m_brake_bias

def packet_telemetry_management(self, packet):
    self.angle = -packet.m_car_telemetry_data[self.index].m_steer*180
    self.gear = packet.m_car_telemetry_data[self.index].m_gear
    self.speed = packet.m_car_telemetry_data[self.index].m_speed
    self.rpm = packet.m_car_telemetry_data[self.index].m_engine_rpm
    self.revLightPercent = packet.m_car_telemetry_data[self.index].m_rev_lights_percent
    self.revLightBitValue = packet.m_car_telemetry_data[self.index].m_rev_lights_bit_value
    self.tyres_temp = packet.m_car_telemetry_data[self.index].m_tyres_inner_temperature
    
def packet_car_status_management(self, packet):
    self.ers_pourcentage = round(packet.m_car_status_data[self.index].m_ers_store_energy/40_000)
    self.ers_mode = packet.m_car_status_data[self.index].m_ers_deploy_mode
    self.vehicleFiaFlag = packet.m_car_status_data[self.index].m_vehicle_fia_flags

def update_labels(self):
    if self.gear == 0:
        self.gear = "N"
    elif self.gear == -1:
        self.gear = "R"    
    
    self.labels = [self.gear, self.speed, self.lap_num, self.rpm, conversion(self.last_lap_time), self.brake_bias, self.ers_mode, self.sc_delta]+self.tyres_temp[:]
    for i,element in enumerate(self.list_text_elements):
        element.label = self.labels[i]

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

def port_selection(dictionnary_settings, self):
    win = Toplevel()
    win.grab_set()
    win.wm_title("Port Selection")
    Label(win, text="Receiving PORT :", font=("Arial", 16)).grid(row=0, column=0, sticky="we", padx=30)
    e = Entry(win, font=("Arial", 16))
    e.insert(0, self.listener.port)
    e.grid(row=1, column=0, padx=30)

    def button():
        if not e.get().isdigit() or not 1000 <= int(e.get()) <= 65536:
            Message(win, text="The PORT must be an integer between 1000 and 65536", fg="red", font=("Arial", 16)).grid(
                row=3, column=0)
        else:
            self.PORT = int(e.get())
            self.listener.socket.close()
            self.listener.port = self.PORT
            self.listener.reset()
            Label(win, text="").grid(row=3, column=0)
            dictionnary_settings["port"] = str(self.PORT)
            with open(script_directory+"/settings.txt", "w") as f:
                json.dump(dictionnary_settings, f)
            win.destroy()

    win.bind('<Return>', lambda e: button())
    win.bind('<KP_Enter>', lambda e: button())
    b = Button(win, text="Confirm", font=("Arial", 16), command=button)
    b.grid(row=2, column=0, pady=10)
    b = Button(win, text="Reset wheel", font=("Arial", 16), command=self.reset)
    b.grid(row=3, column=0, pady=10)

def UDP_Redirect(dictionnary_settings, self):
    win = Toplevel()
    win.grab_set()
    win.wm_title("UDP Redirect")
    var1 = IntVar(value=dictionnary_settings["redirect_active"])
    checkbutton = Checkbutton(win, text="UDP Redirect", variable=var1, onvalue=1, offvalue=0)
    checkbutton.grid(row=0, column=0, sticky="W", padx=30, pady=10)
    Label(win, text="IP Address", font=("Arial", 16), justify=LEFT).grid(row=1, column=0, pady=10)
    e1 = Entry(win, font=("Arial", 16))
    e1.insert(0, dictionnary_settings["ip_adress"])
    e1.grid(row=2, column=0)
    Label(win, text="Port", font=("Arial", 16)).grid(row=3, column=0, pady=(10, 5))
    e2 = Entry(win, font=("Arial", 16))
    e2.insert(0, dictionnary_settings["redirect_port"])
    e2.grid(row=4, column=0, padx=30)

    message : Message = Message(win, text="", fg="red", bg="white", font=("Arial", 16))
    message.grid(row=6, column=0)
    def button():
        redirect_port = e2.get()
        if not redirect_port.isdigit() or not 1000 <= int(redirect_port) <= 65536:
            message.config(text="The PORT must be an integer between 1000 and 65536")
        elif not valid_ip_address(e1.get()):
            message.config(text="IP Address incorrect")
        elif int(redirect_port)==self.listener.port and e1.get()=="127.0.0.1" and int(var1.get()):
            message.config(text="Can't redirect datas to localhost on the same port")
        else:
            self.listener.port = int(self.PORT)
            self.listener.redirect = int(var1.get())
            self.listener.adress = e1.get()
            self.listener.redirect_port = int(e2.get())
            self.listener.reset()
            Label(win, text="").grid(row=3, column=0)

            dictionnary_settings["redirect_active"] = var1.get()
            dictionnary_settings["ip_adress"] = e1.get()
            dictionnary_settings["redirect_port"] = e2.get()
            with open("settings.txt", "w") as f:
                json.dump(dictionnary_settings, f)
            win.destroy()

    win.bind('<Return>', lambda e: button())
    win.bind('<KP_Enter>', lambda e: button())
    b = Button(win, text="Confirm", font=("Arial", 16), command=button)
    b.grid(row=5, column=0, pady=10)

def valid_ip_address(adress):
    s = adress.split(".")
    drapeau = len(s)==4
    for element in s:
        if not (element.isdigit() and 0<=int(element)<=255):
            drapeau = False
    return drapeau