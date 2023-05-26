## Importing Libraries
from Definition import *    # file extensions, EnumToString conversion
from Plot import Plotter

import os, sys, pathlib, fnmatch
import shutil as st

import openseespy.opensees as ops

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class Analyzer:
    def __init__(self, *args, **kwargs):
        self.folderLoc = r'C:\Users\kaiso\OneDrive\Documents\GitHub\Autobuilder-3.0\Test Files'

        # self.mainFileLoc = args[0].fileLoc
        # self.folderLoc = self.mainFileLoc.replace('.ab', '')
        # self.SAPFolderLoc = self.folderLoc + FileExtension.SAPModels

    def generateResponseSpectrum(self, gmFileLoc, periods):
        ''' Generate response spectrum given acceleration time history in g'''

        cols = ['Time (s)', 'Acceleration']

        # 1. read time history file --------------------------------
        df_gm = pd.read_csv(gmFileLoc, names=cols, delimiter='\t', skiprows=1)

        dt = float(df_gm['Time (s)'].diff().iloc[1])   # find time interval assuming constant sampling interval
        gm_acc = df_gm['Acceleration'].to_numpy()
        numPts = len(df_gm.index)
        gmName = gmFileLoc.split('\\')[-1].rstrip('.txt')

        # Initializations --------------------------------
        GM_SPECTRA = pd.DataFrame(columns=['Period(s)','Sa(g)'])

        # 2. Spectra Generation --------------------------------
        print('Generating Spectra for GM: {}'.format(gmName))   
        
        for ii, T in enumerate(periods):    # iterate over the specified periods
            # 3. Perform SDOF dynamic analysis for each specified period and obtain the max response -------------------
            # Storing Periods
            GM_SPECTRA.loc[ii,'Period(s)'] = T
                    
            # Setting modelbuilder
            ops.model('basic', '-ndm', 3, '-ndf', 6)
            
            # Setting SDOF Variables        
            g = Constants.g             # value of g
            L = 1.0                     # Length 
            d = 2                       # Diameter
            r = d/2                     # Radius
            A = np.pi*(r**2)            # Area
            E = 1.0                     # Elastic Modulus
            G = 1.0                     # Shear Modulus
            I3 = np.pi*(r**4)/4         # Moment of Inertia (zz)                
            J = np.pi*(r**4)/2          # Polar Moment of Inertia
            I2 = np.pi*(r**4)/4         # Moment of Inertia (yy)
            K = 3*E*I3/(L**3)           # Stiffness 
            M = K*(T**2)/4/(np.pi**2)   # Mass (function of T[period] and K)
            omega = np.sqrt(K/M)     # Natural Frequency
            Tn = 2*np.pi/omega          # Natural Period
                    
            # Creating nodes
            node1_coords = [0.0, 0.0, 0.0]
            ops.node(1, *node1_coords)
            node2_coords = [0.0, 0.0, L]
            ops.node(2, *node2_coords)
            
            # Transformation
            transfTag = 1
            ops.geomTransf('Linear',transfTag,0.0,1.0,0.0)
            
            # Setting boundary condition
            node1_constrs = [1,1,1,1,1,1]
            ops.fix(1, *node1_constrs)
            
            # Defining materials
            ops.uniaxialMaterial("Elastic", 11, E)
            
            # Defining elements
            ops.element("elasticBeamColumn",12,1,2,A,E,G,J,I2,I3,1)
            
            # Defining mass
            ops.mass(2,M,M,0.0,0.0,0.0,0.0)
            
            print('     Calculating Spectral Ordinate for Period = {} secs'.format(np.round(T,3)))
        
            # Storing GM Histories
            gm = gm_acc
            tag = 2
            X_TRANSLATION = 1

            # Unidirectional Uniform Earthquake ground motion (uniform acceleration input at all support nodes)
            ops.timeSeries('Path', tag, '-dt', dt, '-values', *list(gm), '-factor', g)
            # Creating UniformExcitation load pattern
            ops.pattern('UniformExcitation', tag, X_TRANSLATION, '-accel', tag)
            
            # Defining Damping
            # Applying Rayleigh Damping from $xDamp
            # D=$alphaM*M + $betaKcurr*Kcurrent + $betaKcomm*KlastCommit + $beatKinit*$Kinitial
            xDamp 		= 0.05							# 5% damping ratio
            alphaM 		= 0.								# M-prop. damping; D = alphaM*M
            betaKcurr 	= 0.         						# K-proportional damping;      +beatKcurr*KCurrent
            betaKcomm 	= float(2.*xDamp/omega)   		    # K-prop. damping parameter;   +betaKcomm*KlastCommitt
            betaKinit 	= 0.        						# initial-stiffness proportional damping      +beatKinit*Kini
            ops.rayleigh(alphaM,betaKcurr,betaKinit,betaKcomm) # RAYLEIGH damping
                    
            # Creating the analysis
            ops.wipeAnalysis()			            # clear previously-define analysis parameters
            ops.constraints("Plain")                # how to handle boundary conditions
            ops.numberer("Plain")                   # renumber dof's to minimize band-width (optimization), if you want to
            ops.system('BandGeneral')               # how to store and solve the system of equations in the analysis
            ops.algorithm('Linear')	                # use Linear algorithm for linear analysis
            ops.integrator('Newmark', 0.5, 0.25)    # determine the next time step for an analysis
            ops.analysis("Transient")
            
            # Variables (Can alter the speed of analysis)
            dtAnalysis    = dt
            TmaxAnalysis  = int(dt*numPts)
            tCurrent      = ops.getTime()
            time          = [tCurrent]
            ok            = 0
            
            # Initializations of response
            u1            = [0.0]
                    
            # Performing the transient analysis (Performance is slow in this loop, can be altered by changing the parameters) --- wtf does this loop do?
            while ok == 0 and tCurrent < TmaxAnalysis:
                ok = ops.analyze(1, dtAnalysis)
                        
                tCurrent = ops.getTime()
                time.append(tCurrent)
                u1.append(ops.nodeDisp(2,1))
                
            # Storing responses
            DISP_X = np.array(u1)
            
            # Storing Spectra
            GM_SPECTRA.loc[ii,'Sa(g)']= np.max(DISP_X) * (omega**2)/g
            print(GM_SPECTRA.head())
            ops.wipe()

        # Writing Spectra to Files ----------------------------------------
        path_spectra = self.folderLoc + '\Spectra'               
        if not os.path.exists(path_spectra):
            os.makedirs(path_spectra)            
        GM_SPECTRA.to_csv('{}\{}_Spectra.txt'.format(path_spectra, gmName), sep=' ',header=True,index=False)
            
        # Plotting Spectra ----------------------------------------
        title = 'Response Spectrum - {}'.format(gmName)
        plotter = Plotter('Period(s)', 'Sa(g)', title, '.-')
        for index, row in GM_SPECTRA.iterrows():
            plotter.addxData(row['Period(s)'])
            plotter.addyData(row['Sa(g)'])
        plotter.show()
        plotter.save(self.folderLoc + '\\' + gmName + '.png')

if __name__ == '__main__':
    analyzer = Analyzer()

    gmPath = r"D:\Documents\UofT\Seismic Design Team\2023\Autobuilder\2023_GM2.txt"
    periods = [0.01*i for i in range(1,30)]

    analyzer.generateResponseSpectrum(gmPath, periods)