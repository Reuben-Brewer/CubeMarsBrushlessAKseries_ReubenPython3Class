# -*- coding: utf-8 -*-

'''
Reuben Brewer, Ph.D.
reuben.brewer@gmail.com
www.reubotics.com

Apache 2 License
Software Revision A, 2/01/2023

Verified working on: Python 3.8 for Windows 10 64-bit.
(most likely also works on Ubuntu 20.04 and Raspberry Pi Buster but haven't tested yet. Does not work on Mac.)
'''

__author__ = 'reuben.brewer'

#########################################################

##########################
import sys
print("CubeMarsBrushlessAKseries_ReubenPython3Class, running in Python version: " + str(sys.version))
if sys.version_info[0] < 3:
    print("CubeMarsBrushlessAKseries_ReubenPython3Class ERROR: This code is not supported in Python 2!")
    exit()
##########################

import os
import platform
import time
import datetime
import math
import struct
import collections
import inspect #To enable 'TellWhichFileWereIn'
import threading
import traceback
#########################################################

#########################################################

##########################
import serial #___IMPORTANT: pip install pyserial (NOT pip install serial).
from serial.tools import list_ports
##########################

##########################
global ftd2xx_IMPORTED_FLAG
ftd2xx_IMPORTED_FLAG = 0

try:
    import ftd2xx #https://pypi.org/project/ftd2xx/ 'pip install ftd2xx', current version is 1.3.1 as of 05/06/22. For SetAllFTDIdevicesLatencyTimer function
    ftd2xx_IMPORTED_FLAG = 1

except:
    exceptions = sys.exc_info()[0]
    print("**********")
    print("********** CubeMarsBrushlessAKseries_ReubenPython3Class __init__: ERROR, failed to import ftdtxx, Exceptions: %s" % exceptions + " ********** ")
    print("**********")
##########################

##########################
from PyCRC.CRCCCITT import CRCCCITT as PyCRC_CRC16_CCITT_XMODEM #have to install "sudo pip install pythoncrc" (NOT pycrc). Also have the installation wheel file if needed.
##########################

#########################################################

#########################################################
from tkinter import *
import tkinter.font as tkFont
from tkinter import ttk
#########################################################

#########################################################
import queue as Queue
#########################################################

#########################################################
from future.builtins import input as input
######################################################### #"sudo pip3 install future" (Python 3)

#########################################################
import platform
if platform.system() == "Windows":
    import ctypes
    winmm = ctypes.WinDLL('winmm')
    winmm.timeBeginPeriod(1) #Set minimum timer resolution to 1ms so that time.sleep(0.001) behaves properly.
#########################################################

class CubeMarsBrushlessAKseries_ReubenPython3Class(Frame): #Subclass the Tkinter Frame

    ##########################################################################################################
    ##########################################################################################################
    def __init__(self, setup_dict): #Subclass the Tkinter Frame

        print("#################### CubeMarsBrushlessAKseries_ReubenPython3Class __init__ starting. ####################")

        #########################################################
        #########################################################
        self.EXIT_PROGRAM_FLAG = 0
        self.OBJECT_CREATED_SUCCESSFULLY_FLAG = 0
        self.EnableInternal_MyPrint_Flag = 0
        self.DedicatedTxThread_still_running_flag = 0

        self.SerialBaudRate = 921600
        self.SerialTimeoutSeconds = 0.5
        self.SerialParity = serial.PARITY_NONE
        self.SerialStopBits = serial.STOPBITS_ONE
        self.SerialByteSize = serial.EIGHTBITS
        self.SerialConnectedFlag = -11111
        self.SerialPortNameCorrespondingToCorrectSerialNumber = "default"

        self.SerialRxThread_still_running_flag = 0
        self.SerialRxBufferSize = 100
        self.SerialTxBufferSize = 100

        self.CurrentTime_CalculatedFromDedicatedTxThread = -11111.0
        self.StartingTime_CalculatedFromDedicatedTxThread = -11111.0
        self.LastTime_CalculatedFromDedicatedTxThread = -11111.0
        self.DataStreamingFrequency_CalculatedFromDedicatedTxThread = -11111.0
        self.DataStreamingDeltaT_CalculatedFromDedicatedTxThread = -11111.0

        self.CurrentTime_CalculatedFromDedicatedRxThread = -11111.0
        self.LastTime_CalculatedFromDedicatedRxThread = -11111.0
        self.StartingTime_CalculatedFromDedicatedRxThread = -11111.0
        self.DataStreamingFrequency_CalculatedFromDedicatedRxThread = -11111.0
        self.DataStreamingDeltaT_CalculatedFromDedicatedRxThread = -11111.0

        self.LastTimeHeartbeatWasSent_CalculatedFromDedicatedTxThread = -11111.0

        self.CommandTypeString_AcceptableValuesList = ["DutyCycle", "CurrentAmps", "SpeedElectricalRPM", "PositionDeg", "Home"]

        self.ControlMode_AcceptableValuesList = ["DutyCycle", "CurrentAmps", "SpeedElectricalRPM", "PositionDeg"]

        self.DutyCycle_Min_MotorHardLimit = -100.00
        self.DutyCycle_Max_MotorHardLimit  = 100.00

        #UART Manual, page 34:  Among them, the current value is of int32 type, and the value -60000 to 60000 represents -60 to 60A.
        self.CurrentAmps_Min_MotorHardLimit  = -60.0
        self.CurrentAmps_Max_MotorHardLimit  = 60.0

        #UART Manual, page 38: Among them, the speed is int16 type, and the range -100000 to 100000 represents -100000 to 100000 electrical speed;
        self.SpeedElectricalRPM_Min_MotorHardLimit  = -100000.0
        self.SpeedElectricalRPM_Max_MotorHardLimit  = 100000.0

        #UART Manual, page 37: Among them, the position is int32 type, and the range -360000000 to 360000000 represents the position -36000deg to 36000deg
        self.PositionDeg_Min_MotorHardLimit  = -2147483648.0/1000000.0 #Limit of 32-bit signed int, even though manual says we should be able to get -100.0*360.0deg
        self.PositionDeg_Max_MotorHardLimit  = 2147483647.0/1000000.0 #Limit of 32-bit signed int, even though manual says we should be able to get -100.0*360.0deg

        self.PositionDeg_Received = -11111

        self.HomeMotor_NeedsToBeChangedFlag = 0
        self.StopInAllModes_NeedsToBeChangedFlag = 0

        self.SendCommandToMotor_Queue = Queue.Queue()

        self.MostRecentDataDict = dict()

        self.MessageToSendIncludingCRC16xmodem_IntsList_LAST_SENT = ""
        #########################################################
        #########################################################

        #########################################################
        #########################################################
        if platform.system() == "Linux":

            if "raspberrypi" in platform.uname(): #os.uname() doesn't work in windows
                self.my_platform = "pi"
            else:
                self.my_platform = "linux"

        elif platform.system() == "Windows":
            self.my_platform = "windows"

        elif platform.system() == "Darwin":
            self.my_platform = "mac"

        else:
            self.my_platform = "other"

        print("CubeMarsBrushlessAKseries_ReubenPython3Class __init__: The OS platform is: " + self.my_platform)
        #########################################################
        #########################################################

        #########################################################
        #########################################################
        if "GUIparametersDict" in setup_dict:
            self.GUIparametersDict = setup_dict["GUIparametersDict"]

            #########################################################
            #########################################################
            if "USE_GUI_FLAG" in self.GUIparametersDict:
                self.USE_GUI_FLAG = self.PassThrough0and1values_ExitProgramOtherwise("USE_GUI_FLAG", self.GUIparametersDict["USE_GUI_FLAG"])
            else:
                self.USE_GUI_FLAG = 0

            print("CubeMarsBrushlessAKseries_ReubenPython3Class __init__: USE_GUI_FLAG: " + str(self.USE_GUI_FLAG))
            #########################################################
            #########################################################

            #########################################################
            #########################################################
            if "root" in self.GUIparametersDict:
                self.root = self.GUIparametersDict["root"]
            else:
                print("CubeMarsBrushlessAKseries_ReubenPython3Class __init__: ERROR, must pass in 'root'")
                return
            #########################################################
            #########################################################

            #########################################################
            #########################################################
            if "EnableInternal_MyPrint_Flag" in self.GUIparametersDict:
                self.EnableInternal_MyPrint_Flag = self.PassThrough0and1values_ExitProgramOtherwise("EnableInternal_MyPrint_Flag", self.GUIparametersDict["EnableInternal_MyPrint_Flag"])
            else:
                self.EnableInternal_MyPrint_Flag = 0

            print("CubeMarsBrushlessAKseries_ReubenPython3Class __init__: EnableInternal_MyPrint_Flag: " + str(self.EnableInternal_MyPrint_Flag))
            #########################################################
            #########################################################

            #########################################################
            #########################################################
            if "PrintToConsoleFlag" in self.GUIparametersDict:
                self.PrintToConsoleFlag = self.PassThrough0and1values_ExitProgramOtherwise("PrintToConsoleFlag", self.GUIparametersDict["PrintToConsoleFlag"])
            else:
                self.PrintToConsoleFlag = 1

            print("CubeMarsBrushlessAKseries_ReubenPython3Class __init__: PrintToConsoleFlag: " + str(self.PrintToConsoleFlag))
            #########################################################
            #########################################################

            #########################################################
            #########################################################
            if "NumberOfPrintLines" in self.GUIparametersDict:
                self.NumberOfPrintLines = int(self.PassThroughFloatValuesInRange_ExitProgramOtherwise("NumberOfPrintLines", self.GUIparametersDict["NumberOfPrintLines"], 0.0, 50.0))
            else:
                self.NumberOfPrintLines = 10

            print("CubeMarsBrushlessAKseries_ReubenPython3Class __init__: NumberOfPrintLines: " + str(self.NumberOfPrintLines))
            #########################################################
            #########################################################

            #########################################################
            #########################################################
            if "UseBorderAroundThisGuiObjectFlag" in self.GUIparametersDict:
                self.UseBorderAroundThisGuiObjectFlag = self.PassThrough0and1values_ExitProgramOtherwise("UseBorderAroundThisGuiObjectFlag", self.GUIparametersDict["UseBorderAroundThisGuiObjectFlag"])
            else:
                self.UseBorderAroundThisGuiObjectFlag = 0

            print("CubeMarsBrushlessAKseries_ReubenPython3Class __init__: UseBorderAroundThisGuiObjectFlag: " + str(self.UseBorderAroundThisGuiObjectFlag))
            #########################################################
            #########################################################

            #########################################################
            #########################################################
            if "GUI_ROW" in self.GUIparametersDict:
                self.GUI_ROW = int(self.PassThroughFloatValuesInRange_ExitProgramOtherwise("GUI_ROW", self.GUIparametersDict["GUI_ROW"], 0.0, 1000.0))
            else:
                self.GUI_ROW = 0

            print("CubeMarsBrushlessAKseries_ReubenPython3Class __init__: GUI_ROW: " + str(self.GUI_ROW))
            #########################################################
            #########################################################

            #########################################################
            #########################################################
            if "GUI_COLUMN" in self.GUIparametersDict:
                self.GUI_COLUMN = int(self.PassThroughFloatValuesInRange_ExitProgramOtherwise("GUI_COLUMN", self.GUIparametersDict["GUI_COLUMN"], 0.0, 1000.0))
            else:
                self.GUI_COLUMN = 0

            print("CubeMarsBrushlessAKseries_ReubenPython3Class __init__: GUI_COLUMN: " + str(self.GUI_COLUMN))
            #########################################################
            #########################################################

            #########################################################
            #########################################################
            if "GUI_PADX" in self.GUIparametersDict:
                self.GUI_PADX = int(self.PassThroughFloatValuesInRange_ExitProgramOtherwise("GUI_PADX", self.GUIparametersDict["GUI_PADX"], 0.0, 1000.0))
            else:
                self.GUI_PADX = 0

            print("CubeMarsBrushlessAKseries_ReubenPython3Class __init__: GUI_PADX: " + str(self.GUI_PADX))
            #########################################################
            #########################################################

            #########################################################
            #########################################################
            if "GUI_PADY" in self.GUIparametersDict:
                self.GUI_PADY = int(self.PassThroughFloatValuesInRange_ExitProgramOtherwise("GUI_PADY", self.GUIparametersDict["GUI_PADY"], 0.0, 1000.0))
            else:
                self.GUI_PADY = 0

            print("CubeMarsBrushlessAKseries_ReubenPython3Class __init__: GUI_PADY: " + str(self.GUI_PADY))
            #########################################################
            #########################################################

            #########################################################
            #########################################################
            if "GUI_ROWSPAN" in self.GUIparametersDict:
                self.GUI_ROWSPAN = int(self.PassThroughFloatValuesInRange_ExitProgramOtherwise("GUI_ROWSPAN", self.GUIparametersDict["GUI_ROWSPAN"], 0.0, 1000.0))
            else:
                self.GUI_ROWSPAN = 1

            print("CubeMarsBrushlessAKseries_ReubenPython3Class __init__: GUI_ROWSPAN: " + str(self.GUI_ROWSPAN))
            #########################################################
            #########################################################

            #########################################################
            #########################################################
            if "GUI_COLUMNSPAN" in self.GUIparametersDict:
                self.GUI_COLUMNSPAN = int(self.PassThroughFloatValuesInRange_ExitProgramOtherwise("GUI_COLUMNSPAN", self.GUIparametersDict["GUI_COLUMNSPAN"], 0.0, 1000.0))
            else:
                self.GUI_COLUMNSPAN = 1

            print("CubeMarsBrushlessAKseries_ReubenPython3Class __init__: GUI_COLUMNSPAN: " + str(self.GUI_COLUMNSPAN))
            #########################################################
            #########################################################

            #########################################################
            #########################################################
            if "GUI_STICKY" in self.GUIparametersDict:
                self.GUI_STICKY = str(self.GUIparametersDict["GUI_STICKY"])
            else:
                self.GUI_STICKY = "w"

            print("CubeMarsBrushlessAKseries_ReubenPython3Class __init__: GUI_STICKY: " + str(self.GUI_STICKY))
            #########################################################
            #########################################################

        else:
            self.GUIparametersDict = dict()
            self.USE_GUI_FLAG = 0
            print("CubeMarsBrushlessAKseries_ReubenPython3Class __init__: No GUIparametersDict present, setting USE_GUI_FLAG = " + str(self.USE_GUI_FLAG))

        #print("CubeMarsBrushlessAKseries_ReubenPython3Class __init__: GUIparametersDict = " + str(self.GUIparametersDict))
        #########################################################
        #########################################################

        #########################################################
        #########################################################

        #########################################################
        #########################################################
        if "DesiredSerialNumber" in setup_dict:
            self.DesiredSerialNumber = str(setup_dict["DesiredSerialNumber"])
        else:
            print("CubeMarsBrushlessAKseries_ReubenPython3Class ERROR: Must initialize object with 'DesiredSerialNumber' argument.")
            return

        print("CubeMarsBrushlessAKseries_ReubenPython3Class __init__: DesiredSerialNumber: " + str(self.DesiredSerialNumber))
        #########################################################
        #########################################################

        #########################################################
        #########################################################
        if "ControllerID" in setup_dict:
            try:
                self.ControllerID = int(self.PassThroughFloatValuesInRange_ExitProgramOtherwise("ControllerID", setup_dict["ControllerID"], 1, 1))

            except:
                print("CubeMarsBrushlessAKseries_ReubenPython3Class __init__: ERROR, ControllerID invalid.")
        else:
            self.ControllerID = 1 #Can't determine how ControllerID gets implemented in messages, but only self.ControllerID = 1 works for now.

        print("CubeMarsBrushlessAKseries_ReubenPython3Class __init__: ControllerID: " + str(self.ControllerID))
        #########################################################
        #########################################################

        #########################################################
        #########################################################
        if "NameToDisplay_UserSet" in setup_dict:
            self.NameToDisplay_UserSet = str(setup_dict["NameToDisplay_UserSet"])
        else:
            self.NameToDisplay_UserSet = ""

        print("CubeMarsBrushlessAKseries_ReubenPython3Class __init__: NameToDisplay_UserSet: " + str(self.NameToDisplay_UserSet))
        #########################################################
        #########################################################

        #########################################################
        #########################################################
        if "DedicatedTxThread_TimeToSleepEachLoop" in setup_dict:
            self.DedicatedTxThread_TimeToSleepEachLoop = self.PassThroughFloatValuesInRange_ExitProgramOtherwise("DedicatedTxThread_TimeToSleepEachLoop", setup_dict["DedicatedTxThread_TimeToSleepEachLoop"], 0.001, 100000)

        else:
            self.DedicatedTxThread_TimeToSleepEachLoop = 0.005

        print("CubeMarsBrushlessAKseries_ReubenPython3Class __init__: DedicatedTxThread_TimeToSleepEachLoop: " + str(self.DedicatedTxThread_TimeToSleepEachLoop))
        #########################################################
        #########################################################

        self.DedicatedRxThread_TimeToSleepEachLoop = 0.005 #HARD-CODE THIS FOR 100Hz receiving
        '''
        #########################################################
        #########################################################
        if "DedicatedRxThread_TimeToSleepEachLoop" in setup_dict:
            self.DedicatedRxThread_TimeToSleepEachLoop = self.PassThroughFloatValuesInRange_ExitProgramOtherwise("DedicatedRxThread_TimeToSleepEachLoop", setup_dict["DedicatedRxThread_TimeToSleepEachLoop"], 0.001, 100000)

        else:
            self.DedicatedRxThread_TimeToSleepEachLoop = 0.005

        print("CubeMarsBrushlessAKseries_ReubenPython3Class __init__: DedicatedRxThread_TimeToSleepEachLoop: " + str(self.DedicatedRxThread_TimeToSleepEachLoop))
        #########################################################
        #########################################################
        '''

        #########################################################
        #########################################################
        if "PositionDeg_Min_UserSet" in setup_dict:
            self.PositionDeg_Min_UserSet = self.PassThroughFloatValuesInRange_ExitProgramOtherwise("PositionDeg_Min_UserSet", setup_dict["PositionDeg_Min_UserSet"], self.PositionDeg_Min_MotorHardLimit, self.PositionDeg_Max_MotorHardLimit)

        else:
            self.PositionDeg_Min_UserSet = self.PositionDeg_Min_MotorHardLimit

        print("CubeMarsBrushlessAKseries_ReubenPython3Class: PositionDeg_Min_UserSet: " + str(self.PositionDeg_Min_UserSet))
        #########################################################
        #########################################################
        
        #########################################################
        #########################################################
        if "PositionDeg_Max_UserSet" in setup_dict:
            self.PositionDeg_Max_UserSet = self.PassThroughFloatValuesInRange_ExitProgramOtherwise("PositionDeg_Max_UserSet", setup_dict["PositionDeg_Max_UserSet"], self.PositionDeg_Min_MotorHardLimit, self.PositionDeg_Max_MotorHardLimit)

        else:
            self.PositionDeg_Max_UserSet = self.PositionDeg_Max_MotorHardLimit

        print("CubeMarsBrushlessAKseries_ReubenPython3Class: PositionDeg_Max_UserSet: " + str(self.PositionDeg_Max_UserSet))
        #########################################################
        #########################################################

        #########################################################
        #########################################################
        if "SpeedElectricalRPM_Min_UserSet" in setup_dict:
            self.SpeedElectricalRPM_Min_UserSet = self.PassThroughFloatValuesInRange_ExitProgramOtherwise("SpeedElectricalRPM_Min_UserSet", setup_dict["SpeedElectricalRPM_Min_UserSet"], self.SpeedElectricalRPM_Min_MotorHardLimit, self.SpeedElectricalRPM_Max_MotorHardLimit)

        else:
            self.SpeedElectricalRPM_Min_UserSet = self.SpeedElectricalRPM_Min_MotorHardLimit

        print("CubeMarsBrushlessAKseries_ReubenPython3Class: SpeedElectricalRPM_Min_UserSet: " + str(self.SpeedElectricalRPM_Min_UserSet))
        #########################################################
        #########################################################
        
        #########################################################
        #########################################################
        if "SpeedElectricalRPM_Max_UserSet" in setup_dict:
            self.SpeedElectricalRPM_Max_UserSet = self.PassThroughFloatValuesInRange_ExitProgramOtherwise("SpeedElectricalRPM_Max_UserSet", setup_dict["SpeedElectricalRPM_Max_UserSet"], self.SpeedElectricalRPM_Min_MotorHardLimit, self.SpeedElectricalRPM_Max_MotorHardLimit)

        else:
            self.SpeedElectricalRPM_Max_UserSet = self.SpeedElectricalRPM_Max_MotorHardLimit

        print("CubeMarsBrushlessAKseries_ReubenPython3Class: SpeedElectricalRPM_Max_UserSet: " + str(self.SpeedElectricalRPM_Max_UserSet))
        #########################################################
        #########################################################

        #########################################################
        #########################################################
        if "DutyCycle_Min_UserSet" in setup_dict:
            self.DutyCycle_Min_UserSet = self.PassThroughFloatValuesInRange_ExitProgramOtherwise("DutyCycle_Min_UserSet", setup_dict["DutyCycle_Min_UserSet"], self.DutyCycle_Min_MotorHardLimit, self.DutyCycle_Max_MotorHardLimit)

        else:
            self.DutyCycle_Min_UserSet = self.DutyCycle_Min_MotorHardLimit

        print("CubeMarsBrushlessAKseries_ReubenPython3Class: DutyCycle_Min_UserSet: " + str(self.DutyCycle_Min_UserSet))
        #########################################################
        #########################################################
        
        #########################################################
        #########################################################
        if "DutyCycle_Max_UserSet" in setup_dict:
            self.DutyCycle_Max_UserSet = self.PassThroughFloatValuesInRange_ExitProgramOtherwise("DutyCycle_Max_UserSet", setup_dict["DutyCycle_Max_UserSet"], self.DutyCycle_Min_MotorHardLimit, self.DutyCycle_Max_MotorHardLimit)

        else:
            self.DutyCycle_Max_UserSet = self.DutyCycle_Max_MotorHardLimit

        print("CubeMarsBrushlessAKseries_ReubenPython3Class: DutyCycle_Max_UserSet: " + str(self.DutyCycle_Max_UserSet))
        #########################################################
        #########################################################

        #########################################################
        #########################################################
        if "CurrentAmps_Min_UserSet" in setup_dict:
            self.CurrentAmps_Min_UserSet = self.PassThroughFloatValuesInRange_ExitProgramOtherwise("CurrentAmps_Min_UserSet", setup_dict["CurrentAmps_Min_UserSet"], self.CurrentAmps_Min_MotorHardLimit, self.CurrentAmps_Max_MotorHardLimit)

        else:
            self.CurrentAmps_Min_UserSet = self.CurrentAmps_Min_MotorHardLimit

        print("CubeMarsBrushlessAKseries_ReubenPython3Class: CurrentAmps_Min_UserSet: " + str(self.CurrentAmps_Min_UserSet))
        #########################################################
        #########################################################
        
        #########################################################
        #########################################################
        if "CurrentAmps_Max_UserSet" in setup_dict:
            self.CurrentAmps_Max_UserSet = self.PassThroughFloatValuesInRange_ExitProgramOtherwise("CurrentAmps_Max_UserSet", setup_dict["CurrentAmps_Max_UserSet"], self.CurrentAmps_Min_MotorHardLimit, self.CurrentAmps_Max_MotorHardLimit)

        else:
            self.CurrentAmps_Max_UserSet = self.CurrentAmps_Max_MotorHardLimit

        print("CubeMarsBrushlessAKseries_ReubenPython3Class: CurrentAmps_Max_UserSet: " + str(self.CurrentAmps_Max_UserSet))
        #########################################################
        #########################################################

        #########################################################
        #########################################################
        if "SendCommandToMotor_Queue_MaxSize" in setup_dict:
            self.SendCommandToMotor_Queue_MaxSize = int(self.PassThroughFloatValuesInRange_ExitProgramOtherwise("SendCommandToMotor_Queue_MaxSize", setup_dict["SendCommandToMotor_Queue_MaxSize"], 1.0, 100000.0))

        else:
            self.SendCommandToMotor_Queue_MaxSize = 1

        print("URarm_ReubenPython2and3Class __init__: SendCommandToMotor_Queue_MaxSize: " + str(self.SendCommandToMotor_Queue_MaxSize))
        #########################################################
        #########################################################

        #########################################################
        #########################################################
        if "HeartbeatTimeIntervalSeconds" in setup_dict:
            self.HeartbeatTimeIntervalSeconds = self.PassThroughFloatValuesInRange_ExitProgramOtherwise("HeartbeatTimeIntervalSeconds", setup_dict["HeartbeatTimeIntervalSeconds"], -1.0, 1000000.0)

        else:
            self.HeartbeatTimeIntervalSeconds = -1 #Off

        print("CubeMarsBrushlessAKseries_ReubenPython3Class __init__: HeartbeatTimeIntervalSeconds: " + str(self.HeartbeatTimeIntervalSeconds))
        #########################################################
        #########################################################

        #########################################################
        #########################################################
        if "ControlMode_Starting" in setup_dict:
            ControlMode_Starting_temp = setup_dict["ControlMode_Starting"]

            if ControlMode_Starting_temp not in self.ControlMode_AcceptableValuesList:
                print("SendCommandToMotor_ExternalClassFunction, ERROR: ControlMode_Starting of " + str(ControlMode_Starting_temp) + " is invalid. You must choose from " + str(self.ControlMode_AcceptableValuesList))
                return

            self.ControlMode_Starting = ControlMode_Starting_temp

        else:
            self.ControlMode_Starting = "DutyCycle"

        print("CubeMarsBrushlessAKseries_ReubenPython3Class: ControlMode_Starting: " + str(self.ControlMode_Starting))

        self.ControlMode = self.ControlMode_Starting
        #########################################################
        #########################################################

        #########################################################
        #########################################################
        if "CommandValue_Starting" in setup_dict:
            CommandValue_Starting_temp = setup_dict["CommandValue_Starting"]

            if self.ControlMode_Starting == "PositionDeg":
                self.CommandValue_Starting = self.PassThroughFloatValuesInRange_ExitProgramOtherwise("CommandValue_Starting", CommandValue_Starting_temp, self.PositionDeg_Min_UserSet, self.PositionDeg_Max_UserSet)
                self.PositionDeg_Starting = self.CommandValue_Starting

                self.SpeedElectricalRPM_Starting = 0
                self.DutyCycle_Starting = 0
                self.CurrentAmps_Starting = 0

            elif self.ControlMode_Starting == "SpeedElectricalRPM":
                self.PositionDeg_Starting = 0

                self.CommandValue_Starting = self.PassThroughFloatValuesInRange_ExitProgramOtherwise("CommandValue_Starting", CommandValue_Starting_temp, self.SpeedElectricalRPM_Min_UserSet, self.SpeedElectricalRPM_Max_UserSet)
                self.SpeedElectricalRPM_Starting = self.CommandValue_Starting

                self.DutyCycle_Starting = 0
                self.CurrentAmps_Starting = 0

            elif self.ControlMode_Starting == "DutyCycle":
                self.PositionDeg_Starting = 0
                self.SpeedElectricalRPM_Starting = 0

                self.CommandValue_Starting = self.PassThroughFloatValuesInRange_ExitProgramOtherwise("CommandValue_Starting", CommandValue_Starting_temp,  self.DutyCycle_Min_UserSet, self.DutyCycle_Max_UserSet)
                self.DutyCycle_Starting = self.CommandValue_Starting

                self.CurrentAmps_Starting = 0

            elif self.ControlMode_Starting == "CurrentAmps":
                self.PositionDeg_Starting = 0
                self.SpeedElectricalRPM_Starting = 0
                self.DutyCycle_Starting = 0

                self.CommandValue_Starting = self.PassThroughFloatValuesInRange_ExitProgramOtherwise("CommandValue_Starting", CommandValue_Starting_temp, self.CurrentAmps_Min_UserSet, self.CurrentAmps_Max_UserSet)
                self.CurrentAmps_Starting = self.CommandValue_Starting

        else:
            self.CommandValue_Starting = -11111

            self.PositionDeg_Starting = 0
            self.SpeedElectricalRPM_Starting = 0
            self.DutyCycle_Starting = 0
            self.CurrentAmps_Starting = 0

        print("CubeMarsBrushlessAKseries_ReubenPython3Class: CommandValue_Starting: " + str(self.CommandValue_Starting))
        #########################################################
        #########################################################

        #########################################################
        #########################################################
        self.PositionDeg_NeedsToBeChangedFlag = 1
        self.PositionDeg_ToBeSet = self.PositionDeg_Starting
        self.PositionDeg_GUIscale_NeedsToBeChangedFlag = 0
        #########################################################
        #########################################################
        
        #########################################################
        #########################################################
        self.SpeedElectricalRPM_NeedsToBeChangedFlag = 1
        self.SpeedElectricalRPM_ToBeSet = self.SpeedElectricalRPM_Starting
        self.SpeedElectricalRPM_GUIscale_NeedsToBeChangedFlag = 0
        #########################################################
        #########################################################
        
        #########################################################
        #########################################################
        self.DutyCycle_NeedsToBeChangedFlag = 1
        self.DutyCycle_ToBeSet = self.DutyCycle_Starting
        self.DutyCycle_GUIscale_NeedsToBeChangedFlag = 0
        #########################################################
        #########################################################

        #########################################################
        #########################################################
        self.CurrentAmps_NeedsToBeChangedFlag = 1
        self.CurrentAmps_ToBeSet = self.CurrentAmps_Starting
        self.CurrentAmps_GUIscale_NeedsToBeChangedFlag = 0
        #########################################################
        #########################################################

        #########################################################
        #########################################################
        self.PrintToGui_Label_TextInputHistory_List = [" "]*self.NumberOfPrintLines
        self.PrintToGui_Label_TextInput_Str = ""
        self.GUI_ready_to_be_updated_flag = 0
        #########################################################
        #########################################################

        #########################################################
        #########################################################

        #########################################################
        #########################################################
        try:

            ################
            if ftd2xx_IMPORTED_FLAG == 1:
                self.SetAllFTDIdevicesLatencyTimer()
            ################

            ################
            self.FindAssignAndOpenSerialPort()
            ################

        except:
            exceptions = sys.exc_info()[0]
            print("CubeMarsBrushlessAKseries_ReubenPython3Class __init__: Failed to open serial object, Exceptions: %s" % exceptions)
        #########################################################
        #########################################################

        #########################################################
        #########################################################
        if self.SerialConnectedFlag == 1:

            #########################################################
            #########################################################
            self.DedicatedTxThread_ThreadingObject = threading.Thread(target=self.DedicatedTxThread, args=())
            self.DedicatedTxThread_ThreadingObject.start()
            #########################################################
            #########################################################

            #########################################################
            #########################################################
            self.DedicatedRxThread_ThreadingObject = threading.Thread(target=self.DedicatedRxThread, args=())
            self.DedicatedRxThread_ThreadingObject.start()
            #########################################################
            #########################################################

            #########################################################
            #########################################################
            if self.USE_GUI_FLAG == 1:
                self.StartGUI(self.root)
            #########################################################
            #########################################################

            #########################################################
            #########################################################
            time.sleep(0.25)
            #########################################################
            #########################################################

            #########################################################
            #########################################################
            self.OBJECT_CREATED_SUCCESSFULLY_FLAG = 1
            #########################################################
            #########################################################

        #########################################################
        #########################################################

    ##########################################################################################################
    ##########################################################################################################

    ##########################################################################################################
    ##########################################################################################################
    def __del__(self):
        pass
    ##########################################################################################################
    ##########################################################################################################

    ##########################################################################################################
    ##########################################################################################################
    def PassThrough0and1values_ExitProgramOtherwise(self, InputNameString, InputNumber):

        try:
            InputNumber_ConvertedToFloat = float(InputNumber)
        except:
            exceptions = sys.exc_info()[0]
            print("PassThrough0and1values_ExitProgramOtherwise Error. InputNumber must be a float value, Exceptions: %s" % exceptions)
            input("Press any key to continue")
            sys.exit()

        try:
            if InputNumber_ConvertedToFloat == 0.0 or InputNumber_ConvertedToFloat == 1:
                return InputNumber_ConvertedToFloat
            else:
                input("PassThrough0and1values_ExitProgramOtherwise Error. '" +
                          InputNameString +
                          "' must be 0 or 1 (value was " +
                          str(InputNumber_ConvertedToFloat) +
                          "). Press any key (and enter) to exit.")

                sys.exit()
        except:
            exceptions = sys.exc_info()[0]
            print("PassThrough0and1values_ExitProgramOtherwise Error, Exceptions: %s" % exceptions)
            input("Press any key to continue")
            sys.exit()
    ##########################################################################################################
    ##########################################################################################################

    ##########################################################################################################
    ##########################################################################################################
    def PassThroughFloatValuesInRange_ExitProgramOtherwise(self, InputNameString, InputNumber, RangeMinValue, RangeMaxValue):
        try:
            InputNumber_ConvertedToFloat = float(InputNumber)
        except:
            exceptions = sys.exc_info()[0]
            print("PassThroughFloatValuesInRange_ExitProgramOtherwise Error. InputNumber must be a float value, Exceptions: %s" % exceptions)
            input("Press any key to continue")
            sys.exit()

        try:
            if InputNumber_ConvertedToFloat >= RangeMinValue and InputNumber_ConvertedToFloat <= RangeMaxValue:
                return InputNumber_ConvertedToFloat
            else:
                input("PassThroughFloatValuesInRange_ExitProgramOtherwise Error. '" +
                          InputNameString +
                          "' must be in the range [" +
                          str(RangeMinValue) +
                          ", " +
                          str(RangeMaxValue) +
                          "] (value was " +
                          str(InputNumber_ConvertedToFloat) + "). Press any key (and enter) to exit.")

                sys.exit()
        except:
            exceptions = sys.exc_info()[0]
            print("PassThroughFloatValuesInRange_ExitProgramOtherwise Error, Exceptions: %s" % exceptions)
            input("Press any key to continue")
            sys.exit()
    ##########################################################################################################
    ##########################################################################################################

    ##########################################################################################################
    ##########################################################################################################
    def TellWhichFileWereIn(self):

        #We used to use this method, but it gave us the root calling file, not the class calling file
        #absolute_file_path = os.path.dirname(os.path.realpath(sys.argv[0]))
        #filename = absolute_file_path[absolute_file_path.rfind("\\") + 1:]

        frame = inspect.stack()[1]
        filename = frame[1][frame[1].rfind("\\") + 1:]
        filename = filename.replace(".py","")

        return filename
    ##########################################################################################################
    ##########################################################################################################

    ##########################################################################################################
    ##########################################################################################################
    def getPreciseSecondsTimeStampString(self):
        ts = time.time()

        return ts
    ##########################################################################################################
    ##########################################################################################################

    ##########################################################################################################
    ##########################################################################################################
    def GetMostRecentDataDict(self):

        if self.EXIT_PROGRAM_FLAG == 0:

            self.MostRecentDataDict = dict([("PositionDeg_Received", self.PositionDeg_Received),
                                            ("DataStreamingFrequency_CalculatedFromDedicatedTxThread", self.DataStreamingFrequency_CalculatedFromDedicatedTxThread),
                                            ("DataStreamingFrequency_CalculatedFromDedicatedRxThread", self.DataStreamingFrequency_CalculatedFromDedicatedRxThread),
                                            ("Time", self.CurrentTime_CalculatedFromDedicatedTxThread)])

            #deepcopy is NOT required as MostRecentDataDict only contains numbers (no lists, dicts, etc. that go beyond 1-level).
            return self.MostRecentDataDict.copy()

        else:
            return dict() #So that we're not returning variables during the close-down process.
    ##########################################################################################################
    ##########################################################################################################

    ##########################################################################################################
    ##########################################################################################################
    def UpdateFrequencyCalculation_DedicatedTxThread(self):

        try:
            self.DataStreamingDeltaT_CalculatedFromDedicatedTxThread = self.CurrentTime_CalculatedFromDedicatedTxThread - self.LastTime_CalculatedFromDedicatedTxThread

            if self.DataStreamingDeltaT_CalculatedFromDedicatedTxThread != 0.0:
                self.DataStreamingFrequency_CalculatedFromDedicatedTxThread = 1.0/self.DataStreamingDeltaT_CalculatedFromDedicatedTxThread

            self.LastTime_CalculatedFromDedicatedTxThread = self.CurrentTime_CalculatedFromDedicatedTxThread
        except:
            exceptions = sys.exc_info()[0]
            print("UpdateFrequencyCalculation_DedicatedTxThread ERROR with Exceptions: %s" % exceptions)
            traceback.print_exc()
    ##########################################################################################################
    ##########################################################################################################

    ##########################################################################################################
    ##########################################################################################################
    def UpdateFrequencyCalculation_DedicatedRxThread(self):
        try:
            self.DataStreamingDeltaT_CalculatedFromDedicatedRxThread = self.CurrentTime_CalculatedFromDedicatedRxThread - self.LastTime_CalculatedFromDedicatedRxThread

            if self.DataStreamingDeltaT_CalculatedFromDedicatedRxThread != 0.0:
                self.DataStreamingFrequency_CalculatedFromDedicatedRxThread = 1.0/self.DataStreamingDeltaT_CalculatedFromDedicatedRxThread

            self.LastTime_CalculatedFromDedicatedRxThread = self.CurrentTime_CalculatedFromDedicatedRxThread
        except:
            exceptions = sys.exc_info()[0]
            print("UpdateFrequencyCalculation_DedicatedRxThread ERROR with Exceptions: %s" % exceptions)
            traceback.print_exc()
    ##########################################################################################################
    ##########################################################################################################

    ###########################################################################################################
    ##########################################################################################################
    def SetAllFTDIdevicesLatencyTimer(self, FTDI_LatencyTimer_ToBeSet = 1):

        FTDI_LatencyTimer_ToBeSet = self.LimitNumber_IntOutputOnly(1, 16, FTDI_LatencyTimer_ToBeSet)

        FTDI_DeviceList = ftd2xx.listDevices()
        print("FTDI_DeviceList: " + str(FTDI_DeviceList))

        if FTDI_DeviceList != None:

            for Index, FTDI_SerialNumber in enumerate(FTDI_DeviceList):

                #################################
                try:
                    if sys.version_info[0] < 3: #Python 2
                        FTDI_SerialNumber = str(FTDI_SerialNumber)
                    else:
                        FTDI_SerialNumber = FTDI_SerialNumber.decode('utf-8')

                    FTDI_Object = ftd2xx.open(Index)
                    FTDI_DeviceInfo = FTDI_Object.getDeviceInfo()

                    '''
                    print("FTDI device with serial number " +
                          str(FTDI_SerialNumber) +
                          ", DeviceInfo: " +
                          str(FTDI_DeviceInfo))
                    '''

                except:
                    exceptions = sys.exc_info()[0]
                    print("FTDI device with serial number " + str(FTDI_SerialNumber) + ", could not open FTDI device, Exceptions: %s" % exceptions)
                #################################

                #################################
                try:
                    FTDI_Object.setLatencyTimer(FTDI_LatencyTimer_ToBeSet)
                    time.sleep(0.005)

                    FTDI_LatencyTimer_ReceivedFromDevice = FTDI_Object.getLatencyTimer()
                    FTDI_Object.close()

                    if FTDI_LatencyTimer_ReceivedFromDevice == FTDI_LatencyTimer_ToBeSet:
                        SuccessString = "succeeded!"
                    else:
                        SuccessString = "failed!"

                    print("FTDI device with serial number " +
                          str(FTDI_SerialNumber) +
                          " commanded setLatencyTimer(" +
                          str(FTDI_LatencyTimer_ToBeSet) +
                          "), and getLatencyTimer() returned: " +
                          str(FTDI_LatencyTimer_ReceivedFromDevice) +
                          ", so command " +
                          SuccessString)

                except:
                    exceptions = sys.exc_info()[0]
                    print("FTDI device with serial number " + str(FTDI_SerialNumber) + ", could not set/get Latency Timer, Exceptions: %s" % exceptions)
                #################################

        else:
            print("SetAllFTDIdevicesLatencyTimer ERROR: FTDI_DeviceList is empty, cannot proceed.")
    ##########################################################################################################
    ##########################################################################################################

    ##########################################################################################################
    ##########################################################################################################
    def FindAssignAndOpenSerialPort(self):
        self.MyPrint_WithoutLogFile("FindAssignAndOpenSerialPort: Finding all serial ports...")

        ##############
        SerialNumberToCheckAgainst = str(self.DesiredSerialNumber)
        if self.my_platform == "linux" or self.my_platform == "pi":
            SerialNumberToCheckAgainst = SerialNumberToCheckAgainst[:-1] #The serial number gets truncated by one digit in linux
        else:
            SerialNumberToCheckAgainst = SerialNumberToCheckAgainst
        ##############

        ##############
        SerialPortsAvailable_ListPortInfoObjetsList = serial.tools.list_ports.comports()
        ##############

        ###########################################################################
        SerialNumberFoundFlag = 0
        for SerialPort_ListPortInfoObjet in SerialPortsAvailable_ListPortInfoObjetsList:

            SerialPortName = SerialPort_ListPortInfoObjet[0]
            Description = SerialPort_ListPortInfoObjet[1]
            VID_PID_SerialNumber_Info = SerialPort_ListPortInfoObjet[2]
            self.MyPrint_WithoutLogFile(SerialPortName + ", " + Description + ", " + VID_PID_SerialNumber_Info)

            if VID_PID_SerialNumber_Info.find(SerialNumberToCheckAgainst) != -1 and SerialNumberFoundFlag == 0: #Haven't found a match in a prior loop
                self.SerialPortNameCorrespondingToCorrectSerialNumber = SerialPortName
                SerialNumberFoundFlag = 1 #To ensure that we only get one device
                self.MyPrint_WithoutLogFile("FindAssignAndOpenSerialPort: Found serial number " + SerialNumberToCheckAgainst + " on port " + self.SerialPortNameCorrespondingToCorrectSerialNumber)
                #WE DON'T BREAK AT THIS POINT BECAUSE WE WANT TO PRINT ALL SERIAL DEVICE NUMBERS WHEN PLUGGING IN A DEVICE WITH UNKNOWN SERIAL NUMBE RFOR THE FIRST TIME.
        ###########################################################################

        ###########################################################################
        if(self.SerialPortNameCorrespondingToCorrectSerialNumber != "default"): #We found a match

            try: #Will succeed as long as another program hasn't already opened the serial line.

                self.SerialObject = serial.Serial(self.SerialPortNameCorrespondingToCorrectSerialNumber, self.SerialBaudRate, timeout=self.SerialTimeoutSeconds, parity=self.SerialParity, stopbits=self.SerialStopBits, bytesize=self.SerialByteSize)
                self.SerialObject.set_buffer_size(rx_size=self.SerialRxBufferSize, tx_size=self.SerialTxBufferSize)
                self.SerialConnectedFlag = 1
                self.MyPrint_WithoutLogFile("FindAssignAndOpenSerialPort: Serial is connected and open on port: " + self.SerialPortNameCorrespondingToCorrectSerialNumber)

            except:
                self.SerialConnectedFlag = 0
                self.MyPrint_WithoutLogFile("FindAssignAndOpenSerialPort: ERROR: Serial is physically plugged in but IS IN USE BY ANOTHER PROGRAM.")

        else:
            self.SerialConnectedFlag = -1
            self.MyPrint_WithoutLogFile("FindAssignAndOpenSerialPort: ERROR: Could not find the serial device. IS IT PHYSICALLY PLUGGED IN?")
        ###########################################################################

    ##########################################################################################################
    ##########################################################################################################

    ##########################################################################################################
    ##########################################################################################################
    def LimitNumber_IntOutputOnly(self, min_val, max_val, test_val):
        if test_val > max_val:
            test_val = max_val

        elif test_val < min_val:
            test_val = min_val

        else:
            test_val = test_val

        test_val = int(test_val)

        return test_val
    ##########################################################################################################
    ##########################################################################################################

    ##########################################################################################################
    ##########################################################################################################
    def SendCommandToMotor_ExternalClassFunction(self, CommandValue, CommandTypeString, IgnoreNewDataIfQueueIsFullFlag = 1):

        try:
            if CommandTypeString not in self.CommandTypeString_AcceptableValuesList:
                print("SendCommandToMotor_ExternalClassFunction, ERROR: CommandTypeString of " + str(CommandTypeString) + " is invalid.")

            CommandToSendDict = dict([(CommandTypeString, CommandValue)])

            if self.SendCommandToMotor_Queue.qsize() < self.SendCommandToMotor_Queue_MaxSize:
                self.SendCommandToMotor_Queue.put(CommandToSendDict)

                self.PositionDeg_GUIscale_NeedsToBeChangedFlag = 1
                self.SpeedElectricalRPM_GUIscale_NeedsToBeChangedFlag = 1
                self.DutyCycle_GUIscale_NeedsToBeChangedFlag = 1

            else:
                if IgnoreNewDataIfQueueIsFullFlag != 1:
                    dummy = self.SendCommandToMotor_Queue.get()  # makes room for one more message
                    self.SendCommandToMotor_Queue.put(CommandToSendDict)  # backfills that message with new data

                    self.PositionDeg_GUIscale_NeedsToBeChangedFlag = 1
                    self.SpeedElectricalRPM_GUIscale_NeedsToBeChangedFlag = 1
                    self.DutyCycle_GUIscale_NeedsToBeChangedFlag = 1

        except:
            exceptions = sys.exc_info()[0]
            print("SendCommandToMotor_ExternalClassFunction: Exceptions: %s" % exceptions)
            traceback.print_exc()

    ##########################################################################################################
    ##########################################################################################################

    ##########################################################################################################
    ##########################################################################################################
    def __SendCommandToMotor_InternalClassFunction(self, CommandValue, CommandTypeString, IgnoreNewDataIfQueueIsFullFlag = 1):

        try:
            if CommandTypeString not in self.CommandTypeString_AcceptableValuesList:
                print("__SendCommandToMotor_InternalClassFunction, ERROR: CommandTypeString of " + str(CommandTypeString) + " is invalid.")

            CommandToSendDict = dict([(CommandTypeString, CommandValue)])

            if self.SendCommandToMotor_Queue.qsize() < self.SendCommandToMotor_Queue_MaxSize:
                self.SendCommandToMotor_Queue.put(CommandToSendDict)

            else:
                if IgnoreNewDataIfQueueIsFullFlag != 1:
                    dummy = self.SendCommandToMotor_Queue.get()  # makes room for one more message
                    self.SendCommandToMotor_Queue.put(CommandToSendDict)  # backfills that message with new data

        except:
            exceptions = sys.exc_info()[0]
            print("__SendCommandToMotor_InternalClassFunction: Exceptions: %s" % exceptions)
            traceback.print_exc()

    ##########################################################################################################
    ##########################################################################################################

    ##########################################################################################################
    ##########################################################################################################
    ##########################################################################################################
    def __CreateMessageByteArrayObjectAndTxCommandToMotor_InternalClassFunction(self, CommandValue, CommandTypeString, PrintAllBytesForDebuggingFlag = 0):

        ##########################################################################################################
        ##########################################################################################################
        try:
            ##########################################################################################################

            ###################################
            if CommandTypeString not in self.CommandTypeString_AcceptableValuesList:
                print("__CreateMessageByteArrayObjectAndTxCommandToMotor_InternalClassFunction, ERROR: CommandTypeString of " + str(CommandTypeString) + " is invalid.")
                return
            ###################################

            ###################################
            if CommandTypeString == "DutyCycle":
                MessagePrefixHexIntsList = [0x02, 0x05, 0x05]
                CommandValueScaleFactor = 1000
                CommandValueLimited = self.LimitNumber_IntOutputOnly(self.DutyCycle_Min_UserSet, self.DutyCycle_Max_UserSet, CommandValue)
            ###################################

            ###################################
            elif CommandTypeString == "CurrentAmps":
                MessagePrefixHexIntsList = [0x02, 0x05, 0x06]
                CommandValueScaleFactor = 1000
                CommandValueLimited = self.LimitNumber_IntOutputOnly(self.CurrentAmps_Min_UserSet, self.CurrentAmps_Max_UserSet, CommandValue)
            ###################################

            ###################################
            elif CommandTypeString == "SpeedElectricalRPM":
                MessagePrefixHexIntsList = [0x02, 0x05, 0x08]
                CommandValueScaleFactor = 1
                CommandValueLimited = self.LimitNumber_IntOutputOnly(self.SpeedElectricalRPM_Min_UserSet, self.SpeedElectricalRPM_Max_UserSet, CommandValue)
            ###################################

            ###################################
            elif CommandTypeString == "PositionDeg":
                MessagePrefixHexIntsList = [0x02, 0x05, 0x09]
                CommandValueScaleFactor = 1000000
                CommandValueLimited = self.LimitNumber_IntOutputOnly(self.PositionDeg_Min_UserSet, self.PositionDeg_Max_UserSet, CommandValue)
            ###################################

            ###################################
            elif CommandTypeString == "Home":
                MessagePrefixHexIntsList = [0x02, 0x02, 0x5F, 0x01]
            ##########################################################################################################

            ###################################
            else:
                return
            ###################################

            ###################################
            if CommandTypeString != "Home": #If the command isn't "Home", then add additional data bytes.
                self.ControlMode = CommandTypeString

                CommandValueLimitedAndScaled = CommandValueScaleFactor*CommandValueLimited
                #print("__CreateMessageByteArrayObjectAndTxCommandToMotor_InternalClassFunction, CommandValueLimitedAndScaled = " + str(CommandValueLimitedAndScaled))

                CommandValueLimitedAndScaled_ListOf4bytes = self.ConvertSignedIntTo4bytes(CommandValueLimitedAndScaled)

                MessageToSendWithoutCRCByteHexIntsList = MessagePrefixHexIntsList + CommandValueLimitedAndScaled_ListOf4bytes
            ###################################

            ###################################
            else:
                MessageToSendWithoutCRCByteHexIntsList = MessagePrefixHexIntsList
            ###################################

            ###################################
            if PrintAllBytesForDebuggingFlag == 1:
                print("__CreateMessageByteArrayObjectAndTxCommandToMotor_InternalClassFunction, MessageToSendWithoutCRCByteHexIntsList: " + str(MessageToSendWithoutCRCByteHexIntsList))
            ###################################

            ###################################
            self.AddCRC16xmodemToMessageByteArrayObjectAndTxBytesOverSerial(MessageToSendWithoutCRCByteHexIntsList, PrintAllBytesForDebuggingFlag=PrintAllBytesForDebuggingFlag)
            ###################################

            ##########################################################################################################

        except:
            exceptions = sys.exc_info()[0]
            print("__CreateMessageByteArrayObjectAndTxCommandToMotor_InternalClassFunction: Exceptions: %s" % exceptions)
            traceback.print_exc()

        ##########################################################################################################
        ##########################################################################################################



    ##########################################################################################################
    ##########################################################################################################
    ##########################################################################################################

    ##########################################################################################################
    ##########################################################################################################
    def AddCRC16xmodemToMessageByteArrayObjectAndTxBytesOverSerial(self, MessageToSendWithoutCRC16xmodem_ByteArrayObject, PrintAllBytesForDebuggingFlag = 0):

        try:
            ###################################
            if type(MessageToSendWithoutCRC16xmodem_ByteArrayObject) == bytes:
                MessageToSendWithoutCRC16xmodem_IntsList = self.ConvertByteAarrayObjectToIntsList(MessageToSendWithoutCRC16xmodem_ByteArrayObject)
            else:
                MessageToSendWithoutCRC16xmodem_IntsList = MessageToSendWithoutCRC16xmodem_ByteArrayObject
            ###################################

            ###################################
            #print("AddCRC16xmodemToMessageByteArrayObjectAndTxBytesOverSerial, MessageToSendWithoutCRC16xmodem_IntsList: " + str(MessageToSendWithoutCRC16xmodem_IntsList))
            checksum_CRC16_calculated = (PyCRC_CRC16_CCITT_XMODEM().calculate(bytes(MessageToSendWithoutCRC16xmodem_IntsList[2:])))
            checksum_CRC16_calculated_LoByte = checksum_CRC16_calculated & 0xFF
            checksum_CRC16_calculated_HiByte = checksum_CRC16_calculated >> 8
            ###################################

            ###################################
            MessageToSendIncludingCRC16xmodem_IntsList = list(MessageToSendWithoutCRC16xmodem_IntsList)
            MessageToSendIncludingCRC16xmodem_IntsList.append(checksum_CRC16_calculated_HiByte)
            MessageToSendIncludingCRC16xmodem_IntsList.append(checksum_CRC16_calculated_LoByte)
            MessageToSendIncludingCRC16xmodem_IntsList.append(3) #End Frame Byte
            ###################################

            ###################################
            if PrintAllBytesForDebuggingFlag == 1:
                print("AddCRC16xmodemToMessageByteArrayObjectAndTxBytesOverSerial, MessageToSendIncludingCRC16xmodem_IntsList: " + str(MessageToSendIncludingCRC16xmodem_IntsList))
                for element in MessageToSendIncludingCRC16xmodem_IntsList:
                    print(hex(element))

            self.MessageToSendIncludingCRC16xmodem_IntsList_LAST_SENT = MessageToSendIncludingCRC16xmodem_IntsList
            self.SerialObject.write(MessageToSendIncludingCRC16xmodem_IntsList)
            ###################################
            
        except:
            exceptions = sys.exc_info()[0]
            print("AddCRC16xmodemToMessageByteArrayObjectAndTxBytesOverSerial: Exceptions: %s" % exceptions)
            traceback.print_exc()

    ##########################################################################################################
    ##########################################################################################################

    ##########################################################################################################
    ##########################################################################################################
    def ConvertByteAarrayObjectToIntsList(self, Input_ByteArrayObject):

        if type(Input_ByteArrayObject) != bytes:
            print("ConvertByteAarrayObjectToIntsList ERROR, Input_ByteArrayObject must be type = bytes")
            return list()
        else:
            Output_IntsList = list()
            for element in Input_ByteArrayObject:
                Output_IntsList.append(int(element))

            return Output_IntsList
    ##########################################################################################################
    ##########################################################################################################

    ##########################################################################################################
    ##########################################################################################################
    def ConvertSignedIntTo4bytes(self, MySignedInteger):

        try:

            #################################################
            if sys.version_info[0] < 3: #Python2
                MySignedInteger_ConvertedToBytes = struct.pack('<i', MySignedInteger)
                Byte0_Lowest, Byte1, Byte2, Byte3_Highest = struct.unpack('>BBBB', MySignedInteger_ConvertedToBytes) #The number of B's specifies the number of bytes

                BytesListToReturn = [Byte3_Highest, Byte2, Byte1, Byte0_Lowest]
            #################################################

            #################################################
            else: #Python 3
                MySignedInteger_ConvertedToBytes = MySignedInteger.to_bytes(4, 'big', signed =True)
                BytesListToReturn = []
                for element in MySignedInteger_ConvertedToBytes:
                    BytesListToReturn.append(int(element))
            #################################################

            return BytesListToReturn

        except:
            exceptions = sys.exc_info()[0]
            print("ConvertSignedIntTo4bytes, Exceptions: %s" % exceptions + " ********** ")
            return [-11111, -11111, -11111, -11111]

    ##########################################################################################################
    ##########################################################################################################

    ########################################################################################################## unicorn
    ########################################################################################################## 
    def DedicatedTxThread(self):

        self.MyPrint_WithoutLogFile("Started DedicatedTxThread for CubeMarsBrushlessAKseries_ReubenPython3Class object.")
        
        self.DedicatedTxThread_still_running_flag = 1

        self.StartingTime_CalculatedFromDedicatedTxThread = self.getPreciseSecondsTimeStampString()

        ##########################################################################################################
        if self.CommandValue_Starting != -11111:
            self.__SendCommandToMotor_InternalClassFunction(self.CommandValue_Starting, self.ControlMode_Starting) #unicorn
        ##########################################################################################################

        ##########################################################################################################
        while self.EXIT_PROGRAM_FLAG == 0:

            ###############################################
            ###############################################
            ###############################################
            self.CurrentTime_CalculatedFromDedicatedTxThread = self.getPreciseSecondsTimeStampString() - self.StartingTime_CalculatedFromDedicatedTxThread
            ###############################################
            ###############################################
            ###############################################

            ###############################################
            ###############################################
            ###############################################
            if self.HomeMotor_NeedsToBeChangedFlag == 1:

                if self.SendCommandToMotor_Queue.qsize() > 0:
                    DummyGetValue = self.SendCommandToMotor_Queue.get()

                self.__CreateMessageByteArrayObjectAndTxCommandToMotor_InternalClassFunction(0, "Home", PrintAllBytesForDebuggingFlag=0)

                self.HomeMotor_NeedsToBeChangedFlag = 0
            ###############################################
            ###############################################
            ###############################################

            ###############################################
            ###############################################
            ###############################################
            if self.StopInAllModes_NeedsToBeChangedFlag == 1:

                if self.SendCommandToMotor_Queue.qsize() > 0:
                    DummyGetValue = self.SendCommandToMotor_Queue.get()

                self.__CreateMessageByteArrayObjectAndTxCommandToMotor_InternalClassFunction(0, "DutyCycle", PrintAllBytesForDebuggingFlag=0)

                self.StopInAllModes_NeedsToBeChangedFlag = 0
            ###############################################
            ###############################################
            ###############################################

            ###############################################
            ###############################################
            ###############################################
            if self.SendCommandToMotor_Queue.qsize() > 0:
                try:
                    CommandToSendDict = self.SendCommandToMotor_Queue.get()
                    #print("CommandToSendDict: " + str(CommandToSendDict))

                    ###################
                    if "PositionDeg" in CommandToSendDict:
                        self.PositionDeg_ToBeSet = CommandToSendDict["PositionDeg"]
                        self.__CreateMessageByteArrayObjectAndTxCommandToMotor_InternalClassFunction(self.PositionDeg_ToBeSet, "PositionDeg", PrintAllBytesForDebuggingFlag=0)
                    ###################

                    ###################
                    if "SpeedElectricalRPM" in CommandToSendDict:
                        self.SpeedElectricalRPM_ToBeSet = CommandToSendDict["SpeedElectricalRPM"]
                        self.__CreateMessageByteArrayObjectAndTxCommandToMotor_InternalClassFunction(self.SpeedElectricalRPM_ToBeSet, "SpeedElectricalRPM", PrintAllBytesForDebuggingFlag=0)
                    ###################

                    ###################
                    if "DutyCycle" in CommandToSendDict:
                        self.DutyCycle_ToBeSet = CommandToSendDict["DutyCycle"]
                        self.__CreateMessageByteArrayObjectAndTxCommandToMotor_InternalClassFunction(self.DutyCycle_ToBeSet, "DutyCycle", PrintAllBytesForDebuggingFlag=0)
                    ###################
                    
                    ###################
                    if "CurrentAmps" in CommandToSendDict:
                        self.CurrentAmps_ToBeSet = CommandToSendDict["CurrentAmps"]
                        self.__CreateMessageByteArrayObjectAndTxCommandToMotor_InternalClassFunction(self.CurrentAmps_ToBeSet, "CurrentAmps", PrintAllBytesForDebuggingFlag=0)
                    ###################

                except:
                    exceptions = sys.exc_info()[0]
                    print("CubeMarsBrushlessAKseries_ReubenPython3Class, DedicatedTxThread, Inner Exceptions: %s" % exceptions)
                    traceback.print_exc()

            else:

                if self.HeartbeatTimeIntervalSeconds > 0.0:
                    if self.CurrentTime_CalculatedFromDedicatedTxThread - self.LastTimeHeartbeatWasSent_CalculatedFromDedicatedTxThread >= self.HeartbeatTimeIntervalSeconds:
                        if self.MessageToSendIncludingCRC16xmodem_IntsList_LAST_SENT != "":
                            self.SerialObject.write(self.MessageToSendIncludingCRC16xmodem_IntsList_LAST_SENT)
                            #print("Heartbeat at time = " + str(self.CurrentTime_CalculatedFromDedicatedTxThread))
                            self.LastTimeHeartbeatWasSent_CalculatedFromDedicatedTxThread = self.CurrentTime_CalculatedFromDedicatedTxThread

            ###############################################
            ###############################################
            ###############################################
            
            ############################################### USE THE TIME.SLEEP() TO SET THE LOOP FREQUENCY
            ###############################################
            ###############################################
            self.UpdateFrequencyCalculation_DedicatedTxThread()

            if self.DedicatedTxThread_TimeToSleepEachLoop > 0.0:
                if self.DedicatedTxThread_TimeToSleepEachLoop > 0.001:
                    time.sleep(self.DedicatedTxThread_TimeToSleepEachLoop - 0.000) #The "- 0.001" corrects for slight deviation from intended frequency due to other functions being called.
                else:
                    time.sleep(self.DedicatedTxThread_TimeToSleepEachLoop)
            ###############################################
            ###############################################
            ###############################################

        ##########################################################################################################
        
        self.MyPrint_WithoutLogFile("Finished DedicatedTxThread for CubeMarsBrushlessAKseries_ReubenPython3Class object.")
        
        self.DedicatedTxThread_still_running_flag = 0
    ##########################################################################################################
    ##########################################################################################################

    ########################################################################################################## unicorn
    ##########################################################################################################
    ##########################################################################################################
    def DedicatedRxThread(self):

        self.MyPrint_WithoutLogFile("Started DedicatedRxThread for CubeMarsBrushlessAKseries_ReubenPython3Class object.")
        self.DedicatedRxThread_StillRunningFlag = 1

        self.Message_MotorSendsPositionEvery10mAfterReceiving_HexIntsList = [0x02, 0x02, 0x0B, 0x04, 0x9C, 0x7E, 0x03]
        self.SerialObject.write(bytes(self.Message_MotorSendsPositionEvery10mAfterReceiving_HexIntsList))

        self.StartingTime_CalculatedFromDedicatedRxThread = self.getPreciseSecondsTimeStampString()
        ##########################################################################################################
        ##########################################################################################################
        while self.EXIT_PROGRAM_FLAG == 0:

            ##########################################################################################################
            self.CurrentTime_CalculatedFromDedicatedRxThread = self.getPreciseSecondsTimeStampString() - self.StartingTime_CalculatedFromDedicatedRxThread
            ##########################################################################################################

            try:

                ##########################################################################################################
                #1 0x02 header-frame, 1 data-length byte, N data bytes, 2 bytes CRC16, 1 0x03 end-frame byte
                RxMessage_HeaderEndFrameCombo = self.SerialObject.read_until(b'\x02\x05\x16')
                RxMessage = self.SerialObject.read(7)
                #print("RxMessage: " + str(RxMessage))
                ##########################################################################################################

                ##########################################################################################################
                if len(RxMessage) > 0:

                    try:

                        PositionDeg_Received_TEMP = int.from_bytes(self.ConvertByteAarrayObjectToIntsList(RxMessage[0:4]), 'big', signed=True)/10000.0
                      
                        Checksum_ReconstructedFromReceivedChecksumBytes = (RxMessage[4] << 8) | (RxMessage[5] & 0xFF)
                        Checksum_CalculatedFromReceivedDataBytes = (PyCRC_CRC16_CCITT_XMODEM().calculate(bytes([0x16] + self.ConvertByteAarrayObjectToIntsList(RxMessage[:-3]))))

                        if Checksum_ReconstructedFromReceivedChecksumBytes == Checksum_CalculatedFromReceivedDataBytes:
                            self.PositionDeg_Received = PositionDeg_Received_TEMP
                        else:
                            print("@@@@@@@@@@ RECEIVED CHECKSUM DID NOT MATCH @@@@@@@@@@")
                            self.PositionDeg_Received = -22222

                        ########################################################################################################## USE THE TIME.SLEEP() TO SET THE LOOP FREQUENCY
                        self.UpdateFrequencyCalculation_DedicatedRxThread()

                        if self.DedicatedRxThread_TimeToSleepEachLoop > 0.0:
                            if self.DedicatedRxThread_TimeToSleepEachLoop > 0.001:
                                time.sleep(self.DedicatedRxThread_TimeToSleepEachLoop - 0.000) #The "- 0.001" corrects for slight deviation from intended frequency due to other functions being called.
                            else:
                                time.sleep(self.DedicatedRxThread_TimeToSleepEachLoop)
                        ##########################################################################################################

                    except:
                        exceptions = sys.exc_info()[0]
                        print("CubeMarsBrushlessAKseries_ReubenPython3Class, DedicatedRxThread, Inner Exceptions: %s" % exceptions)
                        traceback.print_exc()
                ##########################################################################################################

            except:
                exceptions = sys.exc_info()[0]
                print("CubeMarsBrushlessAKseries_ReubenPython3Class, DedicatedRxThread, Outer Exceptions: %s" % exceptions)
                traceback.print_exc()
            ##########################################################################################################
            ##########################################################################################################

        self.MyPrint_WithoutLogFile("Finished DedicatedRxThread for CubeMarsBrushlessAKseries_ReubenPython3Class object.")
        self.DedicatedRxThread_StillRunningFlag = 0
    ##########################################################################################################
    ##########################################################################################################
    ##########################################################################################################

    ##########################################################################################################
    ##########################################################################################################
    def ExitProgram_Callback(self):

        print("Exiting all threads for CubeMarsBrushlessAKseries_ReubenPython3Class object")

        self.EXIT_PROGRAM_FLAG = 1

    ##########################################################################################################
    ##########################################################################################################

    ##########################################################################################################
    ##########################################################################################################
    def StartGUI(self, GuiParent):

        self.GUI_Thread_ThreadingObject = threading.Thread(target=self.GUI_Thread, args=(GuiParent,))
        self.GUI_Thread_ThreadingObject.setDaemon(True) #Should mean that the GUI thread is destroyed automatically when the main thread is destroyed.
        self.GUI_Thread_ThreadingObject.start()
    ##########################################################################################################
    ##########################################################################################################

    ##########################################################################################################
    ##########################################################################################################
    def GUI_Thread(self, parent):

        print("Starting the GUI_Thread for CubeMarsBrushlessAKseries_ReubenPython3Class object.")

        ###################################################
        ###################################################
        self.root = parent
        self.parent = parent
        ###################################################
        ###################################################

        ###################################################
        ###################################################
        self.myFrame = Frame(self.root)

        if self.UseBorderAroundThisGuiObjectFlag == 1:
            self.myFrame["borderwidth"] = 2
            self.myFrame["relief"] = "ridge"

        self.myFrame.grid(row = self.GUI_ROW,
                          column = self.GUI_COLUMN,
                          padx = self.GUI_PADX,
                          pady = self.GUI_PADY,
                          rowspan = self.GUI_ROWSPAN,
                          columnspan= self.GUI_COLUMNSPAN,
                          sticky = self.GUI_STICKY)
        ###################################################
        ###################################################

        ###################################################
        ###################################################
        self.TKinter_LightGreenColor = '#%02x%02x%02x' % (150, 255, 150) #RGB
        self.TKinter_LightRedColor = '#%02x%02x%02x' % (255, 150, 150) #RGB
        self.TKinter_LightYellowColor = '#%02x%02x%02x' % (255, 255, 150)  # RGB
        self.TKinter_DefaultGrayColor = '#%02x%02x%02x' % (240, 240, 240)  # RGB
        self.TkinterScaleLabelWidth = 30
        self.TkinterScaleWidth = 10
        self.TkinterScaleLength = 250
        ###################################################
        ###################################################

        ###################################################
        ###################################################
        self.DeviceInfo_Label = Label(self.myFrame, text="Device Info", width=150)
        self.DeviceInfo_Label["text"] = self.NameToDisplay_UserSet
        self.DeviceInfo_Label.grid(row=0, column=0, padx=1, pady=1, columnspan=1, rowspan=1, sticky = "")
        ###################################################
        ###################################################

        ###################################################
        ###################################################
        self.Data_Label = Label(self.myFrame, text="Data_Label", width=150)
        self.Data_Label.grid(row=1, column=0, padx=1, pady=1, columnspan=1, rowspan=1, sticky = "")
        ###################################################
        ###################################################

        ###################################################
        ###################################################
        self.ControlsFrame = Frame(self.myFrame)
        self.ControlsFrame.grid(row = 2, column = 0, padx = 1, pady = 1, rowspan = 1, columnspan = 1, sticky = "")
        ###################################################
        ###################################################

        ###################################################
        ###################################################
        self.ButtonsFrame = Frame(self.ControlsFrame)
        self.ButtonsFrame.grid(row = 0, column = 1, padx = 10, pady = 10, rowspan = 1, columnspan = 1, sticky = "")
        ###################################################
        ###################################################
        
        ###################################################
        ###################################################
        self.HomeMotor_Button = Button(self.ButtonsFrame, text="HomeMotor", state="normal", width=20, command=lambda: self.HomeMotor_Button_Response())
        self.HomeMotor_Button.grid(row=0, column=0, padx=1, pady=1, columnspan=1, rowspan=1)
        ###################################################
        ###################################################

        ###################################################
        ###################################################
        self.StopInAllModes_Button = Button(self.ButtonsFrame, text="Stop", state="normal", bg=self.TKinter_LightRedColor, width=20, command=lambda: self.StopInAllModes_Button_Response())
        self.StopInAllModes_Button.grid(row=0, column=1, padx=1, pady=1, columnspan=1, rowspan=1)
        ###################################################
        ###################################################

        ###################################################
        ###################################################
        self.PositionDeg_GUIscale_LabelObject = Label(self.ControlsFrame, text="PositionDeg", width=self.TkinterScaleLabelWidth)
        self.PositionDeg_GUIscale_LabelObject.grid(row=1, column=0, padx=1, pady=1, columnspan=1, rowspan=1)

        self.PositionDeg_GUIscale_Value = DoubleVar()
        self.PositionDeg_GUIscale_ScaleObject = Scale(self.ControlsFrame,
                                        from_=self.PositionDeg_Min_UserSet,
                                        to=self.PositionDeg_Max_UserSet,
                                        #tickinterval=
                                        orient=HORIZONTAL,
                                        borderwidth=2,
                                        showvalue=True,
                                        width=self.TkinterScaleWidth,
                                        length=self.TkinterScaleLength,
                                        resolution=1,
                                        variable=self.PositionDeg_GUIscale_Value)
        
        self.PositionDeg_GUIscale_ScaleObject.bind('<Button-1>', lambda event: self.PositionDeg_GUIscale_EventResponse(event))
        self.PositionDeg_GUIscale_ScaleObject.bind('<B1-Motion>', lambda event: self.PositionDeg_GUIscale_EventResponse(event))
        self.PositionDeg_GUIscale_ScaleObject.bind('<ButtonRelease-1>', lambda event: self.PositionDeg_GUIscale_EventResponse(event))
        self.PositionDeg_GUIscale_ScaleObject.set(self.PositionDeg_ToBeSet)
        self.PositionDeg_GUIscale_ScaleObject.grid(row=1, column=1, padx=1, pady=1, columnspan=1, rowspan=1)
        ###################################################
        ###################################################

        ###################################################
        ###################################################
        self.SpeedElectricalRPM_GUIscale_LabelObject = Label(self.ControlsFrame, text="SpeedElectricalRPM", width=self.TkinterScaleLabelWidth)
        self.SpeedElectricalRPM_GUIscale_LabelObject.grid(row=2, column=0, padx=1, pady=1, columnspan=1, rowspan=1)

        self.SpeedElectricalRPM_GUIscale_Value = DoubleVar()
        self.SpeedElectricalRPM_GUIscale_ScaleObject = Scale(self.ControlsFrame,
                                        from_=self.SpeedElectricalRPM_Min_UserSet,
                                        to=self.SpeedElectricalRPM_Max_UserSet,
                                        #tickinterval=
                                        orient=HORIZONTAL,
                                        borderwidth=2,
                                        showvalue=True,
                                        width=self.TkinterScaleWidth,
                                        length=self.TkinterScaleLength,
                                        resolution=1,
                                        variable=self.SpeedElectricalRPM_GUIscale_Value)
        
        self.SpeedElectricalRPM_GUIscale_ScaleObject.bind('<Button-1>', lambda event: self.SpeedElectricalRPM_GUIscale_EventResponse(event))
        self.SpeedElectricalRPM_GUIscale_ScaleObject.bind('<B1-Motion>', lambda event: self.SpeedElectricalRPM_GUIscale_EventResponse(event))
        self.SpeedElectricalRPM_GUIscale_ScaleObject.bind('<ButtonRelease-1>', lambda event: self.SpeedElectricalRPM_GUIscale_EventResponse(event))
        self.SpeedElectricalRPM_GUIscale_ScaleObject.set(self.SpeedElectricalRPM_ToBeSet)
        self.SpeedElectricalRPM_GUIscale_ScaleObject.grid(row=2, column=1, padx=1, pady=1, columnspan=1, rowspan=1)
        ###################################################
        ###################################################

        ###################################################
        ###################################################
        self.DutyCycle_GUIscale_LabelObject = Label(self.ControlsFrame, text="DutyCycle", width=self.TkinterScaleLabelWidth)
        self.DutyCycle_GUIscale_LabelObject.grid(row=3, column=0, padx=1, pady=1, columnspan=1, rowspan=1)

        self.DutyCycle_GUIscale_Value = DoubleVar()
        self.DutyCycle_GUIscale_ScaleObject = Scale(self.ControlsFrame,
                                        from_=self.DutyCycle_Min_UserSet,
                                        to=self.DutyCycle_Max_UserSet,
                                        #tickinterval=
                                        orient=HORIZONTAL,
                                        borderwidth=2,
                                        showvalue=True,
                                        width=self.TkinterScaleWidth,
                                        length=self.TkinterScaleLength,
                                        resolution=1,
                                        variable=self.DutyCycle_GUIscale_Value)
        
        self.DutyCycle_GUIscale_ScaleObject.bind('<Button-1>', lambda event: self.DutyCycle_GUIscale_EventResponse(event))
        self.DutyCycle_GUIscale_ScaleObject.bind('<B1-Motion>', lambda event: self.DutyCycle_GUIscale_EventResponse(event))
        self.DutyCycle_GUIscale_ScaleObject.bind('<ButtonRelease-1>', lambda event: self.DutyCycle_GUIscale_EventResponse(event))
        self.DutyCycle_GUIscale_ScaleObject.set(self.DutyCycle_ToBeSet)
        self.DutyCycle_GUIscale_ScaleObject.grid(row=3, column=1, padx=1, pady=1, columnspan=1, rowspan=1)
        ###################################################
        ###################################################

        ###################################################
        ###################################################
        self.CurrentAmps_GUIscale_LabelObject = Label(self.ControlsFrame, text="CurrentAmps", width=self.TkinterScaleLabelWidth)
        self.CurrentAmps_GUIscale_LabelObject.grid(row=4, column=0, padx=1, pady=1, columnspan=1, rowspan=1)

        self.CurrentAmps_GUIscale_Value = DoubleVar()
        self.CurrentAmps_GUIscale_ScaleObject = Scale(self.ControlsFrame,
                                        from_=self.CurrentAmps_Min_UserSet,
                                        to=self.CurrentAmps_Max_UserSet,
                                        #tickinterval=
                                        orient=HORIZONTAL,
                                        borderwidth=2,
                                        showvalue=True,
                                        width=self.TkinterScaleWidth,
                                        length=self.TkinterScaleLength,
                                        resolution=0.001,
                                        variable=self.CurrentAmps_GUIscale_Value)

        self.CurrentAmps_GUIscale_ScaleObject.bind('<Button-1>', lambda event: self.CurrentAmps_GUIscale_EventResponse(event))
        self.CurrentAmps_GUIscale_ScaleObject.bind('<B1-Motion>', lambda event: self.CurrentAmps_GUIscale_EventResponse(event))
        self.CurrentAmps_GUIscale_ScaleObject.bind('<ButtonRelease-1>', lambda event: self.CurrentAmps_GUIscale_EventResponse(event))
        self.CurrentAmps_GUIscale_ScaleObject.set(self.CurrentAmps_ToBeSet)
        self.CurrentAmps_GUIscale_ScaleObject.grid(row=4, column=1, padx=1, pady=1, columnspan=1, rowspan=1)
        ###################################################
        ###################################################

        ###################################################
        ###################################################
        self.PrintToGui_Label = Label(self.myFrame, text="PrintToGui_Label", width=150)
        if self.EnableInternal_MyPrint_Flag == 1:
            self.PrintToGui_Label.grid(row=5, column=0, padx=10, pady=1, columnspan=1, rowspan=10, sticky = "")
        ###################################################
        ###################################################

        ###################################################
        ###################################################
        self.GUI_ready_to_be_updated_flag = 1
        ###################################################
        ###################################################

    ##########################################################################################################
    ##########################################################################################################

    ##########################################################################################################
    ##########################################################################################################
    def HomeMotor_Button_Response(self):

        self.HomeMotor_NeedsToBeChangedFlag = 1

        #self.MyPrint_WithoutLogFile("HomeMotor_Button_Response: Event fired!")

    ##########################################################################################################
    ##########################################################################################################

    ##########################################################################################################
    ##########################################################################################################
    def StopInAllModes_Button_Response(self):

        self.StopInAllModes_NeedsToBeChangedFlag = 1

        #self.MyPrint_WithoutLogFile("StopInAllModes_Button_Response: Event fired!")

    ##########################################################################################################
    ##########################################################################################################

    ##########################################################################################################
    ##########################################################################################################
    def PositionDeg_GUIscale_EventResponse(self, event):

        PositionDeg = self.PositionDeg_GUIscale_Value.get()
        self.__SendCommandToMotor_InternalClassFunction(PositionDeg, "PositionDeg")

    ##########################################################################################################
    ##########################################################################################################

    ##########################################################################################################
    ##########################################################################################################
    def SpeedElectricalRPM_GUIscale_EventResponse(self, event):

        SpeedElectricalRPM = self.SpeedElectricalRPM_GUIscale_Value.get()
        self.__SendCommandToMotor_InternalClassFunction(SpeedElectricalRPM, "SpeedElectricalRPM")

    ##########################################################################################################
    ##########################################################################################################
    
    ##########################################################################################################
    ##########################################################################################################
    def DutyCycle_GUIscale_EventResponse(self, event):

        DutyCycle = self.DutyCycle_GUIscale_Value.get()
        self.__SendCommandToMotor_InternalClassFunction(DutyCycle, "DutyCycle")

    ##########################################################################################################
    ##########################################################################################################

    ##########################################################################################################
    ##########################################################################################################
    def CurrentAmps_GUIscale_EventResponse(self, event):

        CurrentAmps = self.CurrentAmps_GUIscale_Value.get()
        self.__SendCommandToMotor_InternalClassFunction(CurrentAmps, "CurrentAmps")

    ##########################################################################################################
    ##########################################################################################################

    ##########################################################################################################
    ##########################################################################################################
    def GUI_update_clock(self):

        #######################################################
        #######################################################
        #######################################################
        #######################################################
        if self.USE_GUI_FLAG == 1 and self.EXIT_PROGRAM_FLAG == 0:

            #######################################################
            #######################################################
            #######################################################
            if self.GUI_ready_to_be_updated_flag == 1:

                #######################################################
                #######################################################
                try:

                    #######################################################
                    self.Data_Label["text"] = "Time: " + self.ConvertFloatToStringWithNumberOfLeadingNumbersAndDecimalPlaces_NumberOrListInput(self.CurrentTime_CalculatedFromDedicatedTxThread, 0, 3) + \
                                            "\nControlMode: " + self.ControlMode +\
                                            "\nPositionDeg Received: " + self.ConvertFloatToStringWithNumberOfLeadingNumbersAndDecimalPlaces_NumberOrListInput(self.PositionDeg_Received, 0, 3) + \
                                            "\nRx Frequency: " + self.ConvertFloatToStringWithNumberOfLeadingNumbersAndDecimalPlaces_NumberOrListInput(self.DataStreamingFrequency_CalculatedFromDedicatedRxThread, 0, 3) +\
                                            "\tTx Frequency: " + self.ConvertFloatToStringWithNumberOfLeadingNumbersAndDecimalPlaces_NumberOrListInput(self.DataStreamingFrequency_CalculatedFromDedicatedTxThread, 0, 3) + \
                                            "\nSendCommandToMotor_Queue.qsize(): " + str(self.SendCommandToMotor_Queue.qsize()) +\
                                            "\nLast Tx command: " + str(self.MessageToSendIncludingCRC16xmodem_IntsList_LAST_SENT)
                    #######################################################

                    #######################################################
                    if self.PositionDeg_GUIscale_NeedsToBeChangedFlag == 1:
                        self.PositionDeg_GUIscale_ScaleObject.set(self.PositionDeg_ToBeSet)
                        self.PositionDeg_GUIscale_NeedsToBeChangedFlag = 0
                    #######################################################

                    #######################################################
                    if self.SpeedElectricalRPM_GUIscale_NeedsToBeChangedFlag == 1:
                        self.SpeedElectricalRPM_GUIscale_ScaleObject.set(self.SpeedElectricalRPM_ToBeSet)
                        self.SpeedElectricalRPM_GUIscale_NeedsToBeChangedFlag = 0
                    #######################################################
                    
                    #######################################################
                    if self.DutyCycle_GUIscale_NeedsToBeChangedFlag == 1:
                        self.DutyCycle_GUIscale_ScaleObject.set(self.DutyCycle_ToBeSet)
                        self.DutyCycle_GUIscale_NeedsToBeChangedFlag = 0
                    #######################################################
                    
                    #######################################################
                    if self.CurrentAmps_GUIscale_NeedsToBeChangedFlag == 1:
                        self.CurrentAmps_GUIscale_ScaleObject.set(self.CurrentAmps_ToBeSet)
                        self.CurrentAmps_GUIscale_NeedsToBeChangedFlag = 0
                    #######################################################
                    
                    #######################################################
                    self.PrintToGui_Label.config(text=self.PrintToGui_Label_TextInput_Str)
                    #######################################################

                except:
                    exceptions = sys.exc_info()[0]
                    print("CubeMarsBrushlessAKseries_ReubenPython3Class GUI_update_clock ERROR: Exceptions: %s" % exceptions)
                    traceback.print_exc()
                #######################################################
                #######################################################

            #######################################################
            #######################################################
            #######################################################

        #######################################################
        #######################################################
        #######################################################
        #######################################################

    ##########################################################################################################
    ##########################################################################################################

    ##########################################################################################################
    ##########################################################################################################
    def MyPrint_WithoutLogFile(self, input_string):

        input_string = str(input_string)

        if input_string != "":

            #input_string = input_string.replace("\n", "").replace("\r", "")

            ################################ Write to console
            # Some people said that print crashed for pyinstaller-built-applications and that sys.stdout.write fixed this.
            # http://stackoverflow.com/questions/13429924/pyinstaller-packaged-application-works-fine-in-console-mode-crashes-in-window-m
            if self.PrintToConsoleFlag == 1:
                sys.stdout.write(input_string + "\n")
            ################################

            ################################ Write to GUI
            self.PrintToGui_Label_TextInputHistory_List.append(self.PrintToGui_Label_TextInputHistory_List.pop(0)) #Shift the list
            self.PrintToGui_Label_TextInputHistory_List[-1] = str(input_string) #Add the latest value

            self.PrintToGui_Label_TextInput_Str = ""
            for Counter, Line in enumerate(self.PrintToGui_Label_TextInputHistory_List):
                self.PrintToGui_Label_TextInput_Str = self.PrintToGui_Label_TextInput_Str + Line

                if Counter < len(self.PrintToGui_Label_TextInputHistory_List) - 1:
                    self.PrintToGui_Label_TextInput_Str = self.PrintToGui_Label_TextInput_Str + "\n"
            ################################

    ##########################################################################################################
    ##########################################################################################################

    ##########################################################################################################
    ##########################################################################################################
    def ConvertBytesObjectToString(self, InputBytesObject):

        if sys.version_info[0] < 3:  # Python 2
            OutputString = str(InputBytesObject)

        else:
            OutputString = InputBytesObject.decode('utf-8')

        return OutputString
    ##########################################################################################################
    ##########################################################################################################

    ##########################################################################################################
    ##########################################################################################################
    def IsInputList(self, InputToCheck):

        result = isinstance(InputToCheck, list)
        return result
    ##########################################################################################################
    ##########################################################################################################

    ##########################################################################################################
    ##########################################################################################################
    ##########################################################################################################
    ##########################################################################################################
    def ConvertFloatToStringWithNumberOfLeadingNumbersAndDecimalPlaces_NumberOrListInput(self, input, number_of_leading_numbers = 4, number_of_decimal_places = 3):

        number_of_decimal_places = max(1, number_of_decimal_places) #Make sure we're above 1

        ListOfStringsToJoin = []

        ##########################################################################################################
        ##########################################################################################################
        ##########################################################################################################
        if isinstance(input, str) == 1:
            ListOfStringsToJoin.append(input)
        ##########################################################################################################
        ##########################################################################################################
        ##########################################################################################################

        ##########################################################################################################
        ##########################################################################################################
        ##########################################################################################################
        elif isinstance(input, int) == 1 or isinstance(input, float) == 1:
            element = float(input)
            prefix_string = "{:." + str(number_of_decimal_places) + "f}"
            element_as_string = prefix_string.format(element)

            ##########################################################################################################
            ##########################################################################################################
            if element >= 0:
                element_as_string = element_as_string.zfill(number_of_leading_numbers + number_of_decimal_places + 1 + 1)  # +1 for sign, +1 for decimal place
                element_as_string = "+" + element_as_string  # So that our strings always have either + or - signs to maintain the same string length
            else:
                element_as_string = element_as_string.zfill(number_of_leading_numbers + number_of_decimal_places + 1 + 1 + 1)  # +1 for sign, +1 for decimal place
            ##########################################################################################################
            ##########################################################################################################

            ListOfStringsToJoin.append(element_as_string)
        ##########################################################################################################
        ##########################################################################################################
        ##########################################################################################################

        ##########################################################################################################
        ##########################################################################################################
        ##########################################################################################################
        elif isinstance(input, list) == 1:

            if len(input) > 0:
                for element in input: #RECURSION
                    ListOfStringsToJoin.append(self.ConvertFloatToStringWithNumberOfLeadingNumbersAndDecimalPlaces_NumberOrListInput(element, number_of_leading_numbers, number_of_decimal_places))

            else: #Situation when we get a list() or []
                ListOfStringsToJoin.append(str(input))

        ##########################################################################################################
        ##########################################################################################################
        ##########################################################################################################

        ##########################################################################################################
        ##########################################################################################################
        ##########################################################################################################
        elif isinstance(input, tuple) == 1:

            if len(input) > 0:
                for element in input: #RECURSION
                    ListOfStringsToJoin.append("TUPLE" + self.ConvertFloatToStringWithNumberOfLeadingNumbersAndDecimalPlaces_NumberOrListInput(element, number_of_leading_numbers, number_of_decimal_places))

            else: #Situation when we get a list() or []
                ListOfStringsToJoin.append(str(input))

        ##########################################################################################################
        ##########################################################################################################
        ##########################################################################################################

        ##########################################################################################################
        ##########################################################################################################
        ##########################################################################################################
        elif isinstance(input, dict) == 1:

            if len(input) > 0:
                for Key in input: #RECURSION
                    ListOfStringsToJoin.append(str(Key) + ": " + self.ConvertFloatToStringWithNumberOfLeadingNumbersAndDecimalPlaces_NumberOrListInput(input[Key], number_of_leading_numbers, number_of_decimal_places))

            else: #Situation when we get a dict()
                ListOfStringsToJoin.append(str(input))

        ##########################################################################################################
        ##########################################################################################################
        ##########################################################################################################
        else:
            ListOfStringsToJoin.append(str(input))
        ##########################################################################################################
        ##########################################################################################################
        ##########################################################################################################

        ##########################################################################################################
        ##########################################################################################################
        ##########################################################################################################

        ##########################################################################################################
        ##########################################################################################################
        ##########################################################################################################
        if len(ListOfStringsToJoin) > 1:

            ##########################################################################################################
            ##########################################################################################################

            ##########################################################################################################
            StringToReturn = ""
            for Index, StringToProcess in enumerate(ListOfStringsToJoin):

                ################################################
                if Index == 0: #The first element
                    if StringToProcess.find(":") != -1 and StringToProcess[0] != "{": #meaning that we're processing a dict()
                        StringToReturn = "{"
                    elif StringToProcess.find("TUPLE") != -1 and StringToProcess[0] != "(":  # meaning that we're processing a tuple
                        StringToReturn = "("
                    else:
                        StringToReturn = "["

                    StringToReturn = StringToReturn + StringToProcess.replace("TUPLE","") + ", "
                ################################################

                ################################################
                elif Index < len(ListOfStringsToJoin) - 1: #The middle elements
                    StringToReturn = StringToReturn + StringToProcess + ", "
                ################################################

                ################################################
                else: #The last element
                    StringToReturn = StringToReturn + StringToProcess

                    if StringToProcess.find(":") != -1 and StringToProcess[-1] != "}":  # meaning that we're processing a dict()
                        StringToReturn = StringToReturn + "}"
                    elif StringToProcess.find("TUPLE") != -1 and StringToProcess[-1] != ")":  # meaning that we're processing a tuple
                        StringToReturn = StringToReturn + ")"
                    else:
                        StringToReturn = StringToReturn + "]"

                ################################################

            ##########################################################################################################

            ##########################################################################################################
            ##########################################################################################################

        elif len(ListOfStringsToJoin) == 1:
            StringToReturn = ListOfStringsToJoin[0]

        else:
            StringToReturn = ListOfStringsToJoin

        return StringToReturn
        ##########################################################################################################
        ##########################################################################################################
        ##########################################################################################################

    ##########################################################################################################
    ##########################################################################################################
    ##########################################################################################################
    ##########################################################################################################

