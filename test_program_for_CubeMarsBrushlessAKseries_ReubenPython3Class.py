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
from CubeMarsBrushlessAKseries_ReubenPython3Class import *
from MyPrint_ReubenPython2and3Class import *
#########################################################

#########################################################

##########################
import sys
print("Python version: " + str(sys.version))
if sys.version_info[0] < 3:
    print("ERROR: This code is not supported in Python 2!")
    exit()
##########################

import os
import platform
import time
import datetime
import threading
import collections
#########################################################

#########################################################
from tkinter import *
import tkinter.font as tkFont
from tkinter import ttk
#########################################################

#########################################################
import platform
if platform.system() == "Windows":
    import ctypes
    winmm = ctypes.WinDLL('winmm')
    winmm.timeBeginPeriod(1) #Set minimum timer resolution to 1ms so that time.sleep(0.001) behaves properly.
#########################################################

###########################################################################################################
##########################################################################################################
def getPreciseSecondsTimeStampString():
    ts = time.time()

    return ts
##########################################################################################################
##########################################################################################################

##########################################################################################################
##########################################################################################################
##########################################################################################################
##########################################################################################################
def ConvertFloatToStringWithNumberOfLeadingNumbersAndDecimalPlaces_NumberOrListInput(input, number_of_leading_numbers = 4, number_of_decimal_places = 3):

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
                ListOfStringsToJoin.append(ConvertFloatToStringWithNumberOfLeadingNumbersAndDecimalPlaces_NumberOrListInput(element, number_of_leading_numbers, number_of_decimal_places))

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
                ListOfStringsToJoin.append("TUPLE" + ConvertFloatToStringWithNumberOfLeadingNumbersAndDecimalPlaces_NumberOrListInput(element, number_of_leading_numbers, number_of_decimal_places))

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
                ListOfStringsToJoin.append(str(Key) + ": " + ConvertFloatToStringWithNumberOfLeadingNumbersAndDecimalPlaces_NumberOrListInput(input[Key], number_of_leading_numbers, number_of_decimal_places))

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

##########################################################################################################
##########################################################################################################
def ConvertDictToProperlyFormattedStringForPrinting(DictToPrint, NumberOfDecimalsPlaceToUse = 3, NumberOfEntriesPerLine = 1, NumberOfTabsBetweenItems = 3):

    ProperlyFormattedStringForPrinting = ""
    ItemsPerLineCounter = 0

    for Key in DictToPrint:

        if isinstance(DictToPrint[Key], dict): #RECURSION
            ProperlyFormattedStringForPrinting = ProperlyFormattedStringForPrinting + \
                                                 Key + ":\n" + \
                                                 ConvertDictToProperlyFormattedStringForPrinting(DictToPrint[Key], NumberOfDecimalsPlaceToUse, NumberOfEntriesPerLine, NumberOfTabsBetweenItems)

        else:
            ProperlyFormattedStringForPrinting = ProperlyFormattedStringForPrinting + \
                                                 Key + ": " + \
                                                 ConvertFloatToStringWithNumberOfLeadingNumbersAndDecimalPlaces_NumberOrListInput(DictToPrint[Key], 0, NumberOfDecimalsPlaceToUse)

        if ItemsPerLineCounter < NumberOfEntriesPerLine - 1:
            ProperlyFormattedStringForPrinting = ProperlyFormattedStringForPrinting + "\t"*NumberOfTabsBetweenItems
            ItemsPerLineCounter = ItemsPerLineCounter + 1
        else:
            ProperlyFormattedStringForPrinting = ProperlyFormattedStringForPrinting + "\n"
            ItemsPerLineCounter = 0

    return ProperlyFormattedStringForPrinting
##########################################################################################################
##########################################################################################################

##########################################################################################################
##########################################################################################################
def GUI_update_clock():
    global root
    global EXIT_PROGRAM_FLAG
    global GUI_RootAfterCallbackInterval_Milliseconds
    global USE_GUI_FLAG
    global MostRecentDict_Label

    global CubeMarsBrushlessAKseries_ReubenPython3ClassObject
    global CubeMarsBrushlessAKseries_OPEN_FLAG
    global SHOW_IN_GUI_CubeMarsBrushlessAKseries_FLAG
    global CubeMarsBrushlessAKseries_MostRecentDict

    global MyPrint_ReubenPython2and3ClassObject
    global MYPRINT_OPEN_FLAG
    global SHOW_IN_GUI_MYPRINT_FLAG

    if USE_GUI_FLAG == 1:
        if EXIT_PROGRAM_FLAG == 0:
        #########################################################
        #########################################################

            #########################################################
            MostRecentDict_Label["text"] = ConvertDictToProperlyFormattedStringForPrinting(CubeMarsBrushlessAKseries_MostRecentDict,
                                                                                           NumberOfDecimalsPlaceToUse = 3,
                                                                                           NumberOfEntriesPerLine = 1,
                                                                                           NumberOfTabsBetweenItems = 1)
            #########################################################

            #########################################################
            if CubeMarsBrushlessAKseries_OPEN_FLAG == 1 and SHOW_IN_GUI_CubeMarsBrushlessAKseries_FLAG == 1:
                CubeMarsBrushlessAKseries_ReubenPython3ClassObject.GUI_update_clock()
            #########################################################

            #########################################################
            if MYPRINT_OPEN_FLAG == 1 and SHOW_IN_GUI_MYPRINT_FLAG == 1:
                MyPrint_ReubenPython2and3ClassObject.GUI_update_clock()
            #########################################################

            root.after(GUI_RootAfterCallbackInterval_Milliseconds, GUI_update_clock)
        #########################################################
        #########################################################

##########################################################################################################
##########################################################################################################

##########################################################################################################
##########################################################################################################
def ExitProgram_Callback():
    global EXIT_PROGRAM_FLAG

    print("ExitProgram_Callback event fired!")

    EXIT_PROGRAM_FLAG = 1
##########################################################################################################
##########################################################################################################

##########################################################################################################
##########################################################################################################
def GUI_Thread():
    global root
    global root_Xpos
    global root_Ypos
    global root_width
    global root_height
    global GUI_RootAfterCallbackInterval_Milliseconds
    global USE_TABS_IN_GUI_FLAG

    ################################################# KEY GUI LINE
    #################################################
    root = Tk()
    #################################################
    #################################################

    #################################################
    #################################################
    global TabControlObject
    global Tab_MainControls
    global Tab_CubeMarsBrushlessAKseries
    global Tab_MyPrint

    if USE_TABS_IN_GUI_FLAG == 1:
        #################################################
        TabControlObject = ttk.Notebook(root)

        Tab_CubeMarsBrushlessAKseries = ttk.Frame(TabControlObject)
        TabControlObject.add(Tab_CubeMarsBrushlessAKseries, text='   CubeMarsBrushlessAKseries   ')

        Tab_MainControls = ttk.Frame(TabControlObject)
        TabControlObject.add(Tab_MainControls, text='   Main Controls   ')

        Tab_MyPrint = ttk.Frame(TabControlObject)
        TabControlObject.add(Tab_MyPrint, text='   MyPrint Terminal   ')

        TabControlObject.pack(expand=1, fill="both")  # CANNOT MIX PACK AND GRID IN THE SAME FRAME/TAB, SO ALL .GRID'S MUST BE CONTAINED WITHIN THEIR OWN FRAME/TAB.

        ############# #Set the tab header font
        TabStyle = ttk.Style()
        TabStyle.configure('TNotebook.Tab', font=('Helvetica', '12', 'bold'))
        #############
        #################################################
    else:
        #################################################
        Tab_MainControls = root
        Tab_CubeMarsBrushlessAKseries = root
        Tab_MyPrint = root
        #################################################

    #################################################
    #################################################

    #################################################
    global MostRecentDict_Label
    MostRecentDict_Label = Label(Tab_MainControls, text="MostRecentDict_Label", width=120, font=("Helvetica", 10))
    MostRecentDict_Label.grid(row=0, column=0, padx=1, pady=1, columnspan=1, rowspan=1)
    #################################################

    ################################################# THIS BLOCK MUST COME 2ND-TO-LAST IN def GUI_Thread() IF USING TABS.
    root.protocol("WM_DELETE_WINDOW", ExitProgram_Callback)  # Set the callback function for when the window's closed.
    root.title("test_program_for_CubeMarsBrushlessAKseries_ReubenPython3Class")
    root.geometry('%dx%d+%d+%d' % (root_width, root_height, root_Xpos, root_Ypos)) # set the dimensions of the screen and where it is placed
    root.after(GUI_RootAfterCallbackInterval_Milliseconds, GUI_update_clock)
    root.mainloop()
    #################################################

    #################################################  THIS BLOCK MUST COME LAST IN def GUI_Thread() REGARDLESS OF CODE.
    root.quit() #Stop the GUI thread, MUST BE CALLED FROM GUI_Thread
    root.destroy() #Close down the GUI thread, MUST BE CALLED FROM GUI_Thread
    #################################################

##########################################################################################################
##########################################################################################################

##########################################################################################################
##########################################################################################################
if __name__ == '__main__':

    #################################################
    #################################################
    global my_platform

    if platform.system() == "Linux":

        if "raspberrypi" in platform.uname():  # os.uname() doesn't work in windows
            my_platform = "pi"
        else:
            my_platform = "linux"

    elif platform.system() == "Windows":
        my_platform = "windows"

    elif platform.system() == "Darwin":
        my_platform = "mac"

    else:
        my_platform = "other"

    print("The OS platform is: " + my_platform)
    #################################################
    #################################################

    #################################################
    #################################################
    global USE_GUI_FLAG
    USE_GUI_FLAG = 1

    global USE_TABS_IN_GUI_FLAG
    USE_TABS_IN_GUI_FLAG = 1

    global USE_CubeMarsBrushlessAKseries_FLAG
    USE_CubeMarsBrushlessAKseries_FLAG = 1

    global USE_MYPRINT_FLAG
    USE_MYPRINT_FLAG = 1

    global USE_SINUSOIDAL_INPUT_FLAG
    USE_SINUSOIDAL_INPUT_FLAG = 0
    #################################################
    #################################################

    #################################################
    #################################################
    global SHOW_IN_GUI_CubeMarsBrushlessAKseries_FLAG
    SHOW_IN_GUI_CubeMarsBrushlessAKseries_FLAG = 1

    global SHOW_IN_GUI_MYPRINT_FLAG
    SHOW_IN_GUI_MYPRINT_FLAG = 1
    #################################################
    #################################################

    #################################################
    #################################################
    global GUI_ROW_CubeMarsBrushlessAKseries
    global GUI_COLUMN_CubeMarsBrushlessAKseries
    global GUI_PADX_CubeMarsBrushlessAKseries
    global GUI_PADY_CubeMarsBrushlessAKseries
    global GUI_ROWSPAN_CubeMarsBrushlessAKseries
    global GUI_COLUMNSPAN_CubeMarsBrushlessAKseries
    GUI_ROW_CubeMarsBrushlessAKseries = 1

    GUI_COLUMN_CubeMarsBrushlessAKseries = 0
    GUI_PADX_CubeMarsBrushlessAKseries = 1
    GUI_PADY_CubeMarsBrushlessAKseries = 10
    GUI_ROWSPAN_CubeMarsBrushlessAKseries = 1
    GUI_COLUMNSPAN_CubeMarsBrushlessAKseries = 1

    global GUI_ROW_MYPRINT
    global GUI_COLUMN_MYPRINT
    global GUI_PADX_MYPRINT
    global GUI_PADY_MYPRINT
    global GUI_ROWSPAN_MYPRINT
    global GUI_COLUMNSPAN_MYPRINT
    GUI_ROW_MYPRINT = 2

    GUI_COLUMN_MYPRINT = 0
    GUI_PADX_MYPRINT = 1
    GUI_PADY_MYPRINT = 10
    GUI_ROWSPAN_MYPRINT = 1
    GUI_COLUMNSPAN_MYPRINT = 1
    #################################################
    #################################################

    #################################################
    #################################################
    global root
    global TabControlObject
    global Tab_MainControls
    global Tab_CubeMarsBrushlessAKseries
    global Tab_MyPrint

    global EXIT_PROGRAM_FLAG
    EXIT_PROGRAM_FLAG = 0

    global CurrentTime_MainLoopThread
    CurrentTime_MainLoopThread = -11111.0

    global StartingTime_MainLoopThread
    StartingTime_MainLoopThread = -11111.0

    global root_Xpos
    root_Xpos = 900

    global root_Ypos
    root_Ypos = 0

    global root_width
    root_width = 1920 - root_Xpos

    global root_height
    root_height = 1020 - root_Ypos

    global GUI_RootAfterCallbackInterval_Milliseconds
    GUI_RootAfterCallbackInterval_Milliseconds = 30

    global SINUSOIDAL_MOTION_INPUT_ROMtestTimeToPeakAngle
    SINUSOIDAL_MOTION_INPUT_ROMtestTimeToPeakAngle = 2.0

    global SINUSOIDAL_MOTION_INPUT_MinValue
    SINUSOIDAL_MOTION_INPUT_MinValue = -90.0

    global SINUSOIDAL_MOTION_INPUT_MaxValue
    SINUSOIDAL_MOTION_INPUT_MaxValue = 90.0

    global ControlMode_AcceptableValuesList
    ControlMode_AcceptableValuesList = ["DutyCycle", "CurrentAmps", "SpeedElectricalRPM", "PositionDeg"]

    global SINUSOIDAL_CONTROL_MODE
    SINUSOIDAL_CONTROL_MODE = "PositionDeg"
    #################################################
    #################################################

    #################################################
    #################################################
    global CubeMarsBrushlessAKseries_ReubenPython3ClassObject

    global CubeMarsBrushlessAKseries_OPEN_FLAG
    CubeMarsBrushlessAKseries_OPEN_FLAG = -1

    global CubeMarsBrushlessAKseries_MostRecentDict
    CubeMarsBrushlessAKseries_MostRecentDict = dict()

    global CubeMarsBrushlessAKseries_MostRecentDict_PositionDeg_Received
    CubeMarsBrushlessAKseries_MostRecentDict_PositionDeg_Received = -11111.0

    global CubeMarsBrushlessAKseries_MostRecentDict_DataStreamingFrequency_CalculatedFromDedicatedTxThread
    CubeMarsBrushlessAKseries_MostRecentDict_DataStreamingFrequency_CalculatedFromDedicatedTxThread = -11111.0

    global CubeMarsBrushlessAKseries_MostRecentDict_DataStreamingFrequency_CalculatedFromDedicatedRxThread
    CubeMarsBrushlessAKseries_MostRecentDict_DataStreamingFrequency_CalculatedFromDedicatedRxThread = -11111.0

    global CubeMarsBrushlessAKseries_MostRecentDict_Time
    CubeMarsBrushlessAKseries_MostRecentDict_Time = -11111.0
    #################################################
    #################################################

    #################################################
    #################################################
    global MyPrint_ReubenPython2and3ClassObject

    global MYPRINT_OPEN_FLAG
    MYPRINT_OPEN_FLAG = -1
    #################################################
    #################################################

    #################################################  KEY GUI LINE
    #################################################
    if USE_GUI_FLAG == 1:
        print("Starting GUI thread...")
        GUI_Thread_ThreadingObject = threading.Thread(target=GUI_Thread)
        GUI_Thread_ThreadingObject.setDaemon(True) #Should mean that the GUI thread is destroyed automatically when the main thread is destroyed.
        GUI_Thread_ThreadingObject.start()
        time.sleep(0.5)  #Allow enough time for 'root' to be created that we can then pass it into other classes.
    else:
        root = None
        Tab_MainControls = None
        Tab_CubeMarsBrushlessAKseries = None
        Tab_MyPrint = None
    #################################################
    #################################################

    #################################################
    #################################################
    global CubeMarsBrushlessAKseries_ReubenPython3ClassObject_GUIparametersDict
    CubeMarsBrushlessAKseries_ReubenPython3ClassObject_GUIparametersDict = dict([("USE_GUI_FLAG", USE_GUI_FLAG and SHOW_IN_GUI_CubeMarsBrushlessAKseries_FLAG),
                                    ("root", Tab_CubeMarsBrushlessAKseries), #root Tab_CubeMarsBrushlessAKseries
                                    ("EnableInternal_MyPrint_Flag", 1),
                                    ("NumberOfPrintLines", 10),
                                    ("UseBorderAroundThisGuiObjectFlag", 0),
                                    ("GUI_ROW", GUI_ROW_CubeMarsBrushlessAKseries),
                                    ("GUI_COLUMN", GUI_COLUMN_CubeMarsBrushlessAKseries),
                                    ("GUI_PADX", GUI_PADX_CubeMarsBrushlessAKseries),
                                    ("GUI_PADY", GUI_PADY_CubeMarsBrushlessAKseries),
                                    ("GUI_ROWSPAN", GUI_ROWSPAN_CubeMarsBrushlessAKseries),
                                    ("GUI_COLUMNSPAN", GUI_COLUMNSPAN_CubeMarsBrushlessAKseries)])

    global CubeMarsBrushlessAKseries_ReubenPython3ClassObject_setup_dict
    CubeMarsBrushlessAKseries_ReubenPython3ClassObject_setup_dict = dict([("GUIparametersDict", CubeMarsBrushlessAKseries_ReubenPython3ClassObject_GUIparametersDict),
                                                                        ("DesiredSerialNumber", "FTZ7YMDNA"), #CHANGE THIS TO MATCH YOUR UNIQUE USB-to-serial converter
                                                                        ("NameToDisplay_UserSet", "Reuben's Test T-Motor Brushless AK-series"),
                                                                        ("DedicatedTxThread_TimeToSleepEachLoop", 0.002),
                                                                        ("SendPositionSpeedDutyCycleCommandToGripper_Queue_MaxSize", 2),
                                                                        ("PositionDeg_Min_UserSet", -3.0*360.0),
                                                                        ("PositionDeg_Max_UserSet", 3.0*360.0),
                                                                        ("SpeedElectricalRPM_Min_UserSet", -1000.0),
                                                                        ("SpeedElectricalRPM_Max_UserSet", 1000.0),
                                                                        ("DutyCycle_Min_UserSet", -95.0),
                                                                        ("DutyCycle_Max_UserSet", 95.0),
                                                                        ("CurrentAmps_Min_UserSet", -5.0),
                                                                        ("CurrentAmps_Max_UserSet", 5.0),
                                                                        ("HeartbeatTimeIntervalSeconds", 0.75), #-1 to turn off the heartbeart
                                                                        ("ControlMode_Starting", SINUSOIDAL_CONTROL_MODE),
                                                                        ("CommandValue_Starting", 0)])

    if USE_CubeMarsBrushlessAKseries_FLAG == 1:
        try:
            CubeMarsBrushlessAKseries_ReubenPython3ClassObject = CubeMarsBrushlessAKseries_ReubenPython3Class(CubeMarsBrushlessAKseries_ReubenPython3ClassObject_setup_dict)
            CubeMarsBrushlessAKseries_OPEN_FLAG = CubeMarsBrushlessAKseries_ReubenPython3ClassObject.OBJECT_CREATED_SUCCESSFULLY_FLAG

        except:
            exceptions = sys.exc_info()[0]
            print("CubeMarsBrushlessAKseries_ReubenPython3ClassObject __init__: Exceptions: %s" % exceptions, 0)
            traceback.print_exc()
    #################################################
    #################################################

    #################################################
    #################################################
    if USE_MYPRINT_FLAG == 1:

        MyPrint_ReubenPython2and3ClassObject_GUIparametersDict = dict([("USE_GUI_FLAG", USE_GUI_FLAG and SHOW_IN_GUI_MYPRINT_FLAG),
                                                                        ("root", Tab_MyPrint),
                                                                        ("UseBorderAroundThisGuiObjectFlag", 0),
                                                                        ("GUI_ROW", GUI_ROW_MYPRINT),
                                                                        ("GUI_COLUMN", GUI_COLUMN_MYPRINT),
                                                                        ("GUI_PADX", GUI_PADX_MYPRINT),
                                                                        ("GUI_PADY", GUI_PADY_MYPRINT),
                                                                        ("GUI_ROWSPAN", GUI_ROWSPAN_MYPRINT),
                                                                        ("GUI_COLUMNSPAN", GUI_COLUMNSPAN_MYPRINT)])

        MyPrint_ReubenPython2and3ClassObject_setup_dict = dict([("NumberOfPrintLines", 10),
                                                                ("WidthOfPrintingLabel", 200),
                                                                ("PrintToConsoleFlag", 1),
                                                                ("LogFileNameFullPath", os.getcwd() + "//TestLog.txt"),
                                                                ("GUIparametersDict", MyPrint_ReubenPython2and3ClassObject_GUIparametersDict)])

        try:
            MyPrint_ReubenPython2and3ClassObject = MyPrint_ReubenPython2and3Class(MyPrint_ReubenPython2and3ClassObject_setup_dict)
            MYPRINT_OPEN_FLAG = MyPrint_ReubenPython2and3ClassObject.OBJECT_CREATED_SUCCESSFULLY_FLAG

        except:
            exceptions = sys.exc_info()[0]
            print("MyPrint_ReubenPython2and3ClassObject __init__: Exceptions: %s" % exceptions)
            traceback.print_exc()
    #################################################
    #################################################

    #################################################
    #################################################
    if USE_CubeMarsBrushlessAKseries_FLAG == 1 and CubeMarsBrushlessAKseries_OPEN_FLAG != 1:
        print("Failed to open CubeMarsBrushlessAKseries_ReubenPython3Class.")
        ExitProgram_Callback()
    #################################################
    #################################################

    #################################################
    #################################################
    if USE_MYPRINT_FLAG == 1 and MYPRINT_OPEN_FLAG != 1:
        print("Failed to open MyPrint_ReubenPython2and3ClassObject.")
        ExitProgram_Callback()
    #################################################
    #################################################

    #################################################
    #################################################
    print("Starting main loop 'test_program_for_CubeMarsBrushlessAKseries_ReubenPython3Class.")
    StartingTime_MainLoopThread = getPreciseSecondsTimeStampString()

    while(EXIT_PROGRAM_FLAG == 0):

        try:

            ###################################################
            CurrentTime_MainLoopThread = getPreciseSecondsTimeStampString() - StartingTime_MainLoopThread
            ###################################################

            ################################################### GET's
            if CubeMarsBrushlessAKseries_OPEN_FLAG == 1:

                CubeMarsBrushlessAKseries_MostRecentDict = CubeMarsBrushlessAKseries_ReubenPython3ClassObject.GetMostRecentDataDict()

                if "Time" in CubeMarsBrushlessAKseries_MostRecentDict:
                    CubeMarsBrushlessAKseries_MostRecentDict_PositionDeg_Received = CubeMarsBrushlessAKseries_MostRecentDict["PositionDeg_Received"]
                    CubeMarsBrushlessAKseries_MostRecentDict_DataStreamingFrequency_CalculatedFromDedicatedTxThread = CubeMarsBrushlessAKseries_MostRecentDict["DataStreamingFrequency_CalculatedFromDedicatedTxThread"]
                    CubeMarsBrushlessAKseries_MostRecentDict_DataStreamingFrequency_CalculatedFromDedicatedRxThread = CubeMarsBrushlessAKseries_MostRecentDict["DataStreamingFrequency_CalculatedFromDedicatedRxThread"]

                    CubeMarsBrushlessAKseries_MostRecentDict_Time = CubeMarsBrushlessAKseries_MostRecentDict["Time"]

                    #print("CubeMarsBrushlessAKseries_MostRecentDict_Time: " + str(CubeMarsBrushlessAKseries_MostRecentDict_Time))
            ###################################################

            ################################################### SET's
            if CubeMarsBrushlessAKseries_OPEN_FLAG == 1:

                if USE_SINUSOIDAL_INPUT_FLAG == 1:
                    time_gain = math.pi / (2.0 * SINUSOIDAL_MOTION_INPUT_ROMtestTimeToPeakAngle)
                    SINUSOIDAL_INPUT_TO_COMMAND = (SINUSOIDAL_MOTION_INPUT_MaxValue + SINUSOIDAL_MOTION_INPUT_MinValue)/2.0 + 0.5*abs(SINUSOIDAL_MOTION_INPUT_MaxValue - SINUSOIDAL_MOTION_INPUT_MinValue)*math.sin(1.0*time_gain*CurrentTime_MainLoopThread)

                    CubeMarsBrushlessAKseries_ReubenPython3ClassObject.SendCommandToMotor_ExternalClassFunction(SINUSOIDAL_INPUT_TO_COMMAND, SINUSOIDAL_CONTROL_MODE)
            ###################################################

            time.sleep(0.002)

        except:
            exceptions = sys.exc_info()[0]
            print("test_program_for_CubeMarsBrushlessAKseries_ReubenPython3Class,exceptions: %s" % exceptions)
            traceback.print_exc()
    #################################################
    #################################################

    ################################################# THIS IS THE EXIT ROUTINE!
    #################################################
    print("Exiting main program 'test_program_for_CubeMarsBrushlessAKseries_ReubenPython3Class.")

    #################################################
    if CubeMarsBrushlessAKseries_OPEN_FLAG == 1:
        CubeMarsBrushlessAKseries_ReubenPython3ClassObject.ExitProgram_Callback()
    #################################################

    #################################################
    if MYPRINT_OPEN_FLAG == 1:
        MyPrint_ReubenPython2and3ClassObject.ExitProgram_Callback()
    #################################################

    #################################################
    #################################################

##########################################################################################################
##########################################################################################################