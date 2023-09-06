"""
This is an example of how to write an input *.data file for MATHIS.
In this specific example, the input file is named 'TestCase.data' which will be located
in a folder named 'TestCase' in the example folder of pymathis
One single function is used (CreateObj()) for each type of object of MATHIS
One can add as many attributes as available for each object
Undefined attribute will get default value.
For Object type, attributes and default value, please refer to MATHIS Documentation
"""

import pymathis.pymathis as pm
import os

FileName = 'TestCase'
Path2Case = os.path.join(os.getcwd(),'TestCase')

#File creation
Case = pm.CreateFile(Path2Case,FileName)
#SImulation parameters
Case = pm.CreateObj(Case,'MISC',TETA0=0, DTETA=1, TIMEUNIT='S', NSAVE=60, ISOTHERMAL=True, GUESS_POWER=True)
Case = pm.CreateObj(Case,'SPEC',ID='CO2',)
Case = pm.CreateObj(Case,'SPEC',ID='H2O')
#boundary conditions
Case = pm.CreateObj(Case,'EXT', TEXT=15, HR = 80)
#zones
Case = pm.CreateObj(Case,'LOC', ID='Room1', ALT=0, AREA=171, HEIGHT=2.525, TINI=20)
# branches
Case = pm.CreateObj(Case,'BRANCH', ID='ExtractionAir', BRANCHTYPE='DEBIT_CONSTANT', LOCIDS=['Room1','EXT'] ,Z1=2.5, Z2=2.5, QV0=2100, CTRLID='CtrlDebit')
Case = pm.CreateObj(Case,'BRANCH', ID='EntreeAir', BRANCHTYPE='ENTREE_FIXE', LOCIDS=['EXT','Room1'], Z1=2.3, Z2=2.3, QV0=1000, DPREF=20)
Case = pm.CreateObj(Case,'BRANCH', ID='Permea_bas', BRANCHTYPE='PERMEABILITE', LOCIDS=['EXT','Room1'],  Z1=0.5, Z2=0.5, QV0=7.5, DPREF=4)
#sources
Case = pm.CreateObj(Case,'HSRC', ID='SourceCO2', HSRCTYPE='STANDARD', LOCID='Room1', MFLUX=0.0000081, SPECIDS='CO2', YKS=1, CTRLID='CtrlNBPersonne')
#Operator
Case = pm.CreateObj(Case,'CTRL', ID='conversionCO2ppmv', CTRLTYPE='OPERATOR', FUNCTION='MAX', QUANTITIES='CONSTANT', CONSTANT=659090.91)
#probes
Case = pm.CreateObj(Case,'CTRL', ID='SondeCO2', CTRLTYPE='PROBE', FUNCTION='VALUE', QUANTITY='YK', SPECID='CO2', LOCID='Room1', CTRLID='conversionCO2ppmv')
Case = pm.CreateObj(Case,'CTRL', ID='SondeHR', CTRLTYPE='PROBE', FUNCTION='VALUE', QUANTITY='HR', LOCID='Room1')
#controler to play wth
Case = pm.CreateObj(Case,'CTRL', ID='CtrlDebit', CTRLTYPE='PASSIVE')
Case = pm.CreateObj(Case,'CTRL', ID='CtrlNBPersonne', CTRLTYPE='PASSIVE')

#closing file
Case.close()

