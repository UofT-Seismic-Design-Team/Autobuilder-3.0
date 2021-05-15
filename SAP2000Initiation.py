import os
import sys
import comtypes.client
import comtypes.gen


#set the following flag to True to attach to an existing instance of the program
#otherwise a new instance of the program will be started
AttachToInstance = False

#set the following flag to True to manually specify the path to SAP2000.exe
#this allows for a connection to a version of SAP2000 other than the latest installation
#otherwise the latest installed version of SAP2000 will be launched
SpecifyPath = True

#if the above flag is set to True, specify the path to SAP2000 below
ProgramPath = 'C:\Program Files\Computers and Structures\SAP2000 22\SAP2000.exe'

if AttachToInstance:
    #attach to a running instance of SAP2000
    try:
        #get the active SapObject
        SapObject = comtypes.client.GetActiveObject("CSI.SAP2000.API.SapObject")

    except (OSError, comtypes.COMError):
        print("No running instance of the program found or failed to attach.")
        sys.exit(-1)
else:
    #create API helper object
    helper = comtypes.client.CreateObject('SAP2000v1.Helper')
    helper = helper.QueryInterface(comtypes.gen.SAP2000v1.cHelper)
    if SpecifyPath:
        try:
            #'create an instance of the SAPObject from the specified path
            SapObject = helper.CreateObject(ProgramPath)

        except (OSError, comtypes.COMError):
            print("Cannot start a new instance of the program from " + ProgramPath)
            sys.exit(-1)
    else:
        try:
            #create an instance of the SAPObject from the latest installed SAP2000
            SapObject = helper.CreateObjectProgID("CSI.SAP2000.API.SapObject")

        except (OSError, comtypes.COMError):
            print("Cannot start a new instance of the program.")
            sys.exit(-1)

    #start SAP2000 application
    SapObject.ApplicationStart()

# start SAP2000
SapModel = SapObject.SapModel

