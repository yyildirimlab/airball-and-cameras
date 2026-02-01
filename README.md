# README

## VR Codes

The [VR Codes](./VR%20Codes/) are the codes for UPBGE (Blender) and ViRMEn.

- The [untitled.blend](./VR%20Codes/Blender/untitled.blend) can be opened in UPBGE and will include all the codes needed.

- The [Virmen](./VR%20Codes/ViRMEn/) files need to be placed in specific locations in the ViRMEn installation:

    1. [move2MiceMiguel.m](./VR%20Codes/ViRMEn/move2MiceMiguel.m) goes into the `movements` directory in your ViRMEn installation.

    2. [newWorld.m](./VR%20Codes/ViRMEn/newWorld.m) and [newWorld.mat](./VR%20Codes/ViRMEn/newWorld.mat) both go in the `experiments` directory in your ViRMEn installation.

## Arduino

Codes in the [Arduino](./Arduino/) directory are to be loaded into Arduino Unos with the Arduino IDE Software. They implement logic for the high-speed cameras for imaging and optogenetics at various image capturing rates.

## OBS Websocket Client

Code in [OBS Websocket Client](./OBS%20Websocket%20Client/) is a GUI that communicates with your OBS software when Websocket is enabled. It begins recording when the specified DAQ signal is on.

## OBIS Laser Controller

Code in [OBIS Laser Controller](./OBIS%20Laser%20Controler/) is a python API to comunicate with OBIS Laser connected via USB. The Blender VR implement this for experiments that need to control the laser.
