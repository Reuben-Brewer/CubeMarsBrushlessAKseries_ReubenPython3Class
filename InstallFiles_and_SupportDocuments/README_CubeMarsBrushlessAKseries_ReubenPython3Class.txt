########################

CubeMarsBrushlessAKseries_ReubenPython3Class

Code (including ability to hook to Tkinter GUI) to control "AK Series Dynamical Modular" motors from CubeMars via UART/asynchronous-serial (does not support CANbus communication).
The official documentation for these motors is quite limited, so the supported funcationality of this class is only a subset of the motor's capabilities.
At this moment position, speed, duty-cycle, and current commands can be sent, and the motor reports back its position at 100Hz.
The motor can also be commanded to reset its "home"/0-position.

Motors verified working with this class:
AK10-9 (https://store.cubemars.com/goods.php?id=1141)
AK60-6 (https://store.cubemars.com/goods.php?id=1136)

Reuben Brewer, Ph.D.

reuben.brewer@gmail.com

www.reubotics.com

Apache 2 License

Software Revision A, 2/01/2023

Verified working on: 
Python 3.8.
Windows 10 64-bit
(most likely also works on Ubuntu 20.04 and Raspberry Pi Buster but haven't tested yet. Does not work on Mac.)

########################  

########################  Set up of communication with the motor
I was unable to communicate over UART with an AK-series motor straight out of the box.
To enable that UART communication, I performed the following:
Step 1: Find the CubeMars wire harness with 3 connectors, composed of:
a 3-pin UART motor-side connector (black, yellow, and green wires),
a 4-pin CAN motor-side connector populated with only 2 wires (blue and white), and
a 5-pin connector that plugs into the R-LINK V2.0 (https://store.cubemars.com/goods.php?id=1140) (receives all 5 wires from the other 2 connectors).
Plug the 3-pin UART and 4-pin CAN connectors into the motor and the 5-pin connector into the R-LINK V2.0.
Step 2: Power the motor with up to 48V (I tested at 24V). Beware of switching power supplies that will see sudden motor decelleration as a fault and shut-down.
Step 3: Examine the motor near its connectors and confirm that the blue LED is on (the motor is receiving power).
Step 4: Open the program "CubeMarstool_V1.31.exe" (downloadable at https://store.cubemars.com/images/file/20230130/CubeMarstool_V1.31.rar).
Note that I was never able to get the other program "R-LINK Config Tool.exe" to communicate with the motor.
Step 5: Press the button in the lower-left of the GUI to switch from Chinese to English.
Step 6: On the right side of the screen, press "Refresh", select the appropriate COMx port from the pull-down menu, and then press "Connect".
Step 7: In the "Application Functions" tab on the left, check that the ControllerID is set to 1 (all example commands for the motor require that)
and that the BaudRate is set to "BAUD_RATE_1M" (1 mega-baud that is actually 921600).
Step 8: (optional) Gains, limits, etc. can be set in the "Parameter Settings" tab on the left side of the GUI.
Be VERY careful here as I made the motor go unstable and also lost communication repeatedly by setting these values improperly.
Step 9: Press the "Write Parameters" tab on the left side of the GUI to save the new settings to the motor.
Step 10: Close the GUI, unpower the motor, and unplug the UART and CAN connectors from the motor.
Step 11: Find the CubeMars wire harness with two 3-pin connectors (the white connector fits into the motor, and the black connector has female-header-receptables).
Step 12: Plug the white 3-pin connector into the motor, and connect the black 3-pin connector to a UART or USB-to-serial cable, following the color coding:
CubeMars black wire (GND) --> UART/USB-to-serial cable GND (black wire for FTDI TTL-232RG).
CubeMars green wire (Tx) --> UART/USB-to-serial cable Rx (yellow wire for FTDI TTL-232RG).
CubeMars yellow wire (Rx) --> UART/USB-to-serial cable Tx (orange wire for FTDI TTL-232RG).
Step 13: If using a USB-to-serial converter, plug it in, open its settings in "Device Manager", and set its Latency Timer to 1ms.
Step 14: Powerup the motor again. The LED beneath the connectors on the motor should switch from red to green once communication is properly established
(note that this LED is separate from the blue LED, and you must look closely at the PCB from an angle to view both LED's).
########################

########################### Python module installation instructions, all OS's

CubeMarsBrushlessAKseries_ReubenPython3Class, ListOfModuleDependencies: ['ftd2xx', 'future.builtins', 'PyCRC.CRCCCITT', 'serial', 'serial.tools']
CubeMarsBrushlessAKseries_ReubenPython3Class, ListOfModuleDependencies_TestProgram: ['MyPrint_ReubenPython2and3Class']
CubeMarsBrushlessAKseries_ReubenPython3Class, ListOfModuleDependencies_NestedLayers: ['future.builtins']
CubeMarsBrushlessAKseries_ReubenPython3Class, ListOfModuleDependencies_All:['ftd2xx', 'future.builtins', 'MyPrint_ReubenPython2and3Class', 'PyCRC.CRCCCITT', 'serial', 'serial.tools']

Note that the code will work just fine without 'ftd2xx' but will be unable to set the Latency Timer programatically for FTDI USB-to-serial converters.

###########################
