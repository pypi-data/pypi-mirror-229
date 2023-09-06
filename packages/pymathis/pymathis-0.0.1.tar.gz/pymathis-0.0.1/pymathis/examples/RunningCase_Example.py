'''
This function is an example of how to uses pymathis.
The input file is the one made using the MakeFileExample.py script
It's named 'TestCase' and output files will be written in 'TestCase' folder
'''

import os
import pymathis.pymathis as pm
import matplotlib.pyplot as plt

def main():
    # Paths and case name
    C_FILE_Path = os.path.join(os.getcwd(), 'TestCase')
    C_FILE = 'TestCase.data'

    #lets go in the right folder and initialise connection with MATHIS
    os.chdir(C_FILE_Path)
    SmartMathis =pm.LoadDll(pm.__file__,C_FILE)

    # Lets fetch the available actuators and their IDs, initialization value is set to 0
    n_passive = pm.get_passive_number(SmartMathis)
    PassiveCtrl_ID = {pm.get_ctrl_ID(SmartMathis, i):[0] for i in range(n_passive)}
    # lets fetch the probes and their IDs
    n_probe = pm.get_probe_number(SmartMathis)
    Probe_ID = {pm.get_probe_ID(SmartMathis, i):[] for i in range(n_probe)}

    # Simulation parameters (start, end, time step) and time loop
    t = 0
    dt = 1
    t_final = 3600*4
    VentOn = 0
    while t < t_final:
        # lets set each controller's position
        for i, key in enumerate(PassiveCtrl_ID):
            pm.give_passive_ctrl(SmartMathis, PassiveCtrl_ID[key][-1], i)

        # Ask MATHIS to compute the current time step
        pm.solve_timestep(SmartMathis, t, dt)

        # lets fetch the new probes' value
        for i,key in enumerate(Probe_ID):
            Probe_ID[key].append(pm.get_probe_ctrl(SmartMathis,i))

        # Lets give the actuators new set points considering the probes values :
        # here is a simple action in which every 1/2hours 10 people are moving either inside or outside
        for key in PassiveCtrl_ID.keys():
            if key == 'CtrlNBPersonne':
                if t%3600<1800: PassiveCtrl_ID[key].append(10)  # 10 people in
                else: PassiveCtrl_ID[key].append(0)             # 0 people in
        # if CO2 probe give values above 800ppm, extracted airlow is at full capacity (define in the cas.data file)
        # a nd below 600ppm, its stopped
        if Probe_ID['SondeCO2'][-1]>800 and not VentOn:
            PassiveCtrl_ID['CtrlDebit'][-1] = 1 #it's a multiplier of the airflow define in the *.data file
            VentOn = 1
        elif Probe_ID['SondeCO2'][-1]<600 and VentOn:
            PassiveCtrl_ID['CtrlDebit'][-1] = 0
            VentOn = 0

        # updating time iteration
        t = t + dt
        # prompt consol report
        if t%1800==0: print('Time : ',t)
    #simulation is done, lets make a plot  of the control and probe
    MakeFinalPlot(PassiveCtrl_ID,Probe_ID)

def MakeFinalPlot(PassiveCtrl_ID,Probe_ID):
    plt.figure()
    plt.subplot(2,1,1)
    plt.plot(PassiveCtrl_ID['CtrlNBPersonne'])
    plt.ylabel(('CtrlNBPersonne'))
    plt.subplot(2, 1, 2)
    plt.plot(Probe_ID['SondeCO2'])
    plt.ylabel(('SondeCO2'))
    plt.xlabel(('Temps'))
    plt.show()

if __name__ == '__main__':
    main()