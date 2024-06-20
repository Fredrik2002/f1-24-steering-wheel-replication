## Replication of SF-24 Steering Wheel with EA F1 24 Telemetry

- [Overview](#overview)
- [Features](#features)
- [Usage](#usage)
  - [Step 1: Run the application](#step1)
  - [Step 2: Send data to the application](#step2)
- [Project Structure](#project-structure)

## 🔍 Overview <a id="overview"></a>
This application replicates the driver's steering wheel movements from the game.

![Capture d'écran 2024-02-03 151858](https://github.com/Fredrik2002/Steering-wheel/assets/86866135/08925157-8dec-45ee-9291-baa7408dd5f4)
![wheel2](https://github.com/Fredrik2002/Steering-wheel/assets/86866135/941385e2-c6c0-45ab-90eb-f38beaa47131)

## 🚀 Features <a id="features"></a>
- ✅ Fully functionnal LEDs
- ✅ Steering wheel rotation according to games inputs
- ✅ ERS state
- ✅ Real time updated datas on the dashboard :
    - Gear
    - Speed
    - Engine RPM
    - Lap number
    - Previous lap time
    - SC & VSC delta times
    - ERS Deployment mode
    - All 4 tyres inner temperature 
- ✅ Setting tab 
    - Select the port you are receiving the datas on
    - Enable UDP Redirection to another IP Address & Port (Ability to redirect to yourself)
- ✅ Font size adjustating to the window size
- ✅ Compatibility with older parsers for previous EA F1 games (F1 23)

## 🔧 Usage <a id="usage"></a>
### <ins>Step 1 : Run the application</ins><a id="step1"></a>
1. Make sure all the required python packages are installed :

```bash
pip install tkinter ttkbootstrap matplotlib numpy
``` 
2. Run *main.py*

### <ins>Step 2 : Send datas to the application </ins> <a id="step2"></a>
Open the F1 Game :
- ➡️ Go to Settings 
- ➡️ Telemetry Settings
- ➡️ Make sure the port in-game matches the port used by the application (20777 by default)
- ➡️ **If your game is connected to the same network as your computer running this application**, the easiest way is to enable the <u>UDP Broadcast</u> setting.
**If not**, you have to enter your public IP address in the <u>IP Address</u> setting.
- ✅ You are then good to go !

## 📘 Project structure <a id="project-structure"></a>
- *LED.py* : Stores classes for REV lights and labels
- ***main.py* : main application you need to run**
- *packet_management.py* : Stores the information received by the game
- *parser202x.py* : Parses the data received for the F1 2x game (default for F1 24)
- *settings.txt* : This files saves the previous connection settings (so you don't have to enter the same port selection and UDP redirection every time). Do not touch unless you know what you are doing
