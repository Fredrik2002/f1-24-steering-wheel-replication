## Replication of SF-23 Steering Wheel working with F1 24 Telemetry

This application replicates the movement of the driver's steering wheel

### Features :
- Fully functionnal LEDs
- Steering wheel rotation according to games inputs
- ERS state
- Real time updated datas on the dashboard :
    - Gear
    - Speed
    - Engine RPM
    - Lap number
    - Previous lap time
    - SC & VSC delta times
    - ERS Deployment mode
    - All 4 tyres inner temperature 
- Setting tab 
    - Select the port you are receiving the datas on
    - Enable UDP Redirection to another IP Address & Port (Ability to redirect to yourself)
- Font size adjustating to the window size

### How to use :
- Install the following packages via the pip install command : ttkbootstrap, matplotlib, numpy
- Run main.py

### To Do List :
- Prendre des captures d'écran avec les paramètres
- Tester une dernière fois