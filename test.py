import os

import sys

import comtypes.client

 

#set the following flag to True to attach to an existing instance of the program

#otherwise a new instance of the program will be started

AttachToInstance = False

 

#set the following flag to True to manually specify the path to SAP2000.exe

#this allows for a connection to a version of SAP2000 other than the latest installation

#otherwise the latest installed version of SAP2000 will be launched

SpecifyPath = False

 

#if the above flag is set to True, specify the path to SAP2000 below

ProgramPath = 'C:\Program Files (x86)\Computers and Structures\SAP2000 22\SAP2000.exe'

 

#full path to the model

#set it to the desired path of your model

APIPath = 'C:\CSiAPIexample'

if not os.path.exists(APIPath):

        try:

            os.makedirs(APIPath)

        except OSError:

            pass

ModelPath = APIPath + os.sep + 'API_1-001.sdb'

ModelPath2 = APIPath + os.sep + 'API_2-001.sdb'

 

if AttachToInstance:

    #attach to a running instance of SAP2000

    try:

        #get the active SapObject

        mySapObject = comtypes.client.GetActiveObject("CSI.SAP2000.API.SapObject")

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

            mySapObject = helper.CreateObject(ProgramPath)

        except (OSError, comtypes.COMError):

            print("Cannot start a new instance of the program from " + ProgramPath)

            sys.exit(-1)

    else:

        try:

            #create an instance of the SAPObject from the latest installed SAP2000

            mySapObject = helper.CreateObjectProgID("CSI.SAP2000.API.SapObject")

        except (OSError, comtypes.COMError):

            print("Cannot start a new instance of the program.")

            sys.exit(-1)

 

    #start SAP2000 application

    mySapObject.ApplicationStart()

    

#create SapModel object

SapModel = mySapObject.SapModel

 

#initialize model

SapModel.InitializeNewModel()

 

#create new blank model

ret = SapModel.File.OpenFile(ModelPath)

 

#save model

ret = SapModel.File.Save(ModelPath2)

 

#run model (this will create the analysis model)

ret = SapModel.Analyze.RunAnalysis()

 

#initialize for Sap2000 results

SapResult= [0,0,0,0,0,0,0]

[PointName1, PointName2, ret] = SapModel.FrameObj.GetPoints(FrameName2, PointName1, PointName2)

 

#get Sap2000 results for load cases 1 through 7

for i in range(0,7):

      NumberResults = 0

      Obj = []

      Elm = []

      ACase = []

      StepType = []

      StepNum = []

      U1 = []

      U2 = []

      U3 = []

      R1 = []

      R2 = []

      R3 = []

      ObjectElm = 0

      ret = SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()

      ret = SapModel.Results.Setup.SetCaseSelectedForOutput(str(i+1))

      if i <= 3:

          [NumberResults, Obj, Elm, ACase, StepType, StepNum, U1, U2, U3, R1, R2, R3, ret] = SapModel.Results.JointDispl(PointName2, ObjectElm, NumberResults, Obj, Elm, ACase, StepType, StepNum, U1, U2, U3, R1, R2, R3)

          SapResult[i] = U3[0]

      else:

          [NumberResults, Obj, Elm, ACase, StepType, StepNum, U1, U2, U3, R1, R2, R3, ret] = SapModel.Results.JointDispl(PointName1, ObjectElm, NumberResults, Obj, Elm, ACase, StepType, StepNum, U1, U2, U3, R1, R2, R3)

          SapResult[i] = U1[0]

 

#close Sap2000

ret = mySapObject.ApplicationExit(False)

SapModel = None

mySapObject = None

 

#fill independent results

IndResult= [0,0,0,0,0,0,0]

IndResult[0] = -0.02639

IndResult[1] = 0.06296

IndResult[2] = 0.06296

IndResult[3] = -0.2963

IndResult[4] = 0.3125

IndResult[5] = 0.11556

IndResult[6] = 0.00651

 

#fill percent difference

PercentDiff = [0,0,0,0,0,0,0]

for i in range(0,7):

      PercentDiff[i] = (SapResult[i] / IndResult[i]) - 1

 

#display results

for i in range(0,7):

      print()

      print(SapResult[i])

      print(IndResult[i])

      print(PercentDiff[i])

