import ctypes as ct
import os, platform

def LoadDll(DLLPath,C_FILE_Path):
    """
    This function load and initiate the communication with MATHIS
    :param DLLPath: the is the absolute or relative path to the smartmathis dll
    :param C_FILE: this is the absolute or relative path the the case (results are written in the same folder)
    :return: the opened smartmathis dll object
    """
    try: #this try/except is only for debuging process when using the code in an pip unpacked manner
        # Load the DLL depending on the os
        if platform.system() == "Windows":
            dll = ct.CDLL(os.path.join(os.path.dirname(DLLPath),'smartmathis.dll'))
        else:
            dll = ct.CDLL(os.path.join(os.path.dirname(DLLPath), 'smartmathis.so'))
        # Initialize solver
        init_solver(dll,C_FILE_Path)
    except:
        # Load the DLL
        if platform.system() == "Windows":
            dll = ct.CDLL(os.path.join(DLLPath,'smartmathis.dll'))
        else:
            dll = ct.CDLL(os.path.join(DLLPath, 'smartmathis.so'))
        # Initialize solver
        init_solver(dll,C_FILE_Path)
    return dll

def CloseDll(dll):
    """
    The function just close the .out file so it can be cleaned or used within the same python code
    :param dll: the opened smartmathis dll
    :return: the *.out file is properly closed
    """
    return dll.STOP_SMARTMATHIS()

def give_passive_ctrl(dll,valuein, tag):
    """
    This function give the position of each passiv controller to mathis
    :param dll: the opened smartmathis dll
    :param valuein: Controller value
    :param tag: Controller position
    :return: none
    """
    # Set the argument and return types
    dll.GET_PASSIVE_CTRL_SMARTMATHIS.argtypes = [ct.POINTER(ct.c_double), ct.POINTER(ct.c_int)]
    dll.GET_PASSIVE_CTRL_SMARTMATHIS.restype = None
    tag = tag + 1
    return dll.GET_PASSIVE_CTRL_SMARTMATHIS(ct.c_double(valuein), ct.c_int(tag))

def get_probe_ctrl(dll,tag):
    """
    This function enable to fetch probes value from mathis
    :param dll: the opened smartmathis dll
    :param tag: the Probes position in mathis file
    :return: the probes values in a numerical format
    """
    # Set the argument and return types
    dll.GIVE_PROBE_CTRL_SMARTMATHIS.argtypes = [ct.POINTER(ct.c_double), ct.POINTER(ct.c_int)]
    dll.GIVE_PROBE_CTRL_SMARTMATHIS.restype = ct.c_double
    tag = tag + 1
    valueout = 0
    valueout = ct.c_double(valueout)
    value_p = ct.pointer(valueout)
    dll.GIVE_PROBE_CTRL_SMARTMATHIS(value_p, ct.c_int(tag))
    return valueout.value

def get_probe_ID(dll,tag):
    """
    This function fetches the Probe's name for each position in mathis' case
    :param dll: the opened smartmathis dll
    :param tag: The probe position
    :return: The Probe name in a string format
    """
    # Set the argument and return types
    dll.GIVE_PROBE_ID_SMARTMATHIS.argtypes = [ct.POINTER(ct.ARRAY(ct.c_char,256)), ct.POINTER(ct.c_int)]
    dll.GIVE_PROBE_ID_SMARTMATHIS.restype = ct.POINTER(ct.ARRAY(ct.c_char,256))
    tag = tag + 1
    valueout = ct.create_string_buffer(b'',256)
    value_p = ct.byref(valueout)
    dll.GIVE_PROBE_ID_SMARTMATHIS(value_p, ct.c_int(tag))
    return valueout.value.decode("utf-8").replace(' ','')

def get_ctrl_ID(dll,tag):
    """
    This function fetches the passiv controller's name for each position in mathis' case
    :param dll: the opened smartmathis dll
    :param tag: the controller position
    :return: The controller name in a string format
    """
    # Set the argument and return types
    dll.GIVE_PASSIVE_ID_SMARTMATHIS.argtypes = [ct.POINTER(ct.ARRAY(ct.c_char,256)), ct.POINTER(ct.c_int)]
    dll.GIVE_PASSIVE_ID_SMARTMATHIS.restype = ct.POINTER(ct.ARRAY(ct.c_char,256))
    tag = tag + 1
    valueout = ct.create_string_buffer(b'',256)
    value_p = ct.byref(valueout)
    dll.GIVE_PASSIVE_ID_SMARTMATHIS(value_p, ct.c_int(tag))
    return valueout.value.decode("utf-8").replace(' ','')

def get_passive_number(dll):
    """
    This function gets the total number of passiv controller in mathis case
    :param dll: the opened smartmathis dll
    :return: integer format
    """
    # Set the return type
    dll.GIVE_PASSIVE_NUMBER_SMARTMATHIS.restype = ct.c_int
    return dll.GIVE_PASSIVE_NUMBER_SMARTMATHIS()

def get_probe_number(dll):
    """
    This function gets the total number of probes in mathis case
    :param dll: the opened smartmathis dll
    :return: integer format
    """
    # Set the return type
    dll.GIVE_PROBE_NUMBER_SMARTMATHIS.restype = ct.c_int
    return dll.GIVE_PROBE_NUMBER_SMARTMATHIS()

def init_solver(dll,file):
    """
    This function initiate mathis dll, the *.data is thus validate through this function
    :param dll: the opened smartmathis dll
    :param file: the *.data and associate path
    :return: none
    """
    # Set the argument type
    dll.INIT_SOLVER_SMARTMATHIS.argtypes = [ct.c_char_p]
    dll.INIT_SOLVER_SMARTMATHIS(file.encode('utf-8'))

def give_weather(dll,vmeteo = 0.,wdir = 0.,text = 20.,hr = 50.,sunrad = 0.,diffrad = 0.,tsky = 0.,tground = 12.,patm = 101300.):
    """
    This function provides MATHIS with outdoor weather conditions for the next timestep calculation
    :param dll: the opened smartmathis dll
    :param vmeteo: wind speed (m/s)
    :param wdir: wind direction () 
    :param text: air temperature (C)
    :param hr: relative humidity (%)
    :param sunrad: normal direct radiation flux (W/m2
    :param diffrad: horizontal diffuse radiation flux (W/m2)
    :param tsky: equivalent sky vault temperature (C)
    :param tground: ground temperature  at a given depth (C)
    :param patm: atmospheric pressure at reference altitude (Pa)
    :return: none
     """
    dll.GET_METEO_SMARTMATHIS.argtypes = [ct.POINTER(ct.c_double), ct.POINTER(ct.c_double), ct.POINTER(ct.c_double), ct.POINTER(ct.c_double), ct.POINTER(ct.c_double), ct.POINTER(ct.c_double), ct.POINTER(ct.c_double), ct.POINTER(ct.c_double), ct.POINTER(ct.c_double)]
    dll.GET_METEO_SMARTMATHIS(ct.c_double(vmeteo),ct.c_double(wdir),ct.c_double(text),ct.c_double(hr),ct.c_double(sunrad),ct.c_double(diffrad),ct.c_double(tsky),ct.c_double(tground),ct.c_double(patm))

def solve_timestep(dll,tasked, dtasked):
    """
    This function ask mathis to solve next time step up to the t+dt
    :param dll: the opened smartmathis dll
    :param tasked: current time
    :param dtasked: time step (can be different from DTETA in the *.data)
    :return: none
    """
    # Set the argument types
    dll.SOLVE_TIMESTEP_SMARTMATHIS.argtypes = [ct.POINTER(ct.c_double), ct.POINTER(ct.c_double)]
    dll.SOLVE_TIMESTEP_SMARTMATHIS(ct.c_double(tasked), ct.c_double(dtasked))

def get_obj_value(dll,objtype,objid,valuename):
    """
    Function for recovering various quantities calculated by MATHIS without using probe controllers
    :param dll:  the opened smartmathis dll
    :param objtype: type of MATHIS object - currently, only the 'LOC' or 'BRANCH' types are implemented
    :param objid: id of MATHIS object
    :param valuename: name of the asked object value.
                      For objtype='LOC': 'DP' (Pa), 'RA' (vol/h), 'RHO' (kg/m3), 'T' (C).
                      For objtype='BRANCH':'QV' (m3/h), 'QM' (kg/s), 'RHOFLOW' (kg/m3), 'DPFLOW' (Pa), 'QV1' (m3/h), 'QV2' (m3/h)
    :return: float format
    """
    # Set the argument types
    dll.GIVE_OBJ_VALUE_SMARTMATHIS.argtypes = [ct.c_char_p,ct.c_char_p,ct.c_char_p,ct.POINTER(ct.c_int)]
    dll.GIVE_OBJ_VALUE_SMARTMATHIS.restype = ct.c_double
    err=ct.c_int(0)
    objvalue=dll.GIVE_OBJ_VALUE_SMARTMATHIS(objtype.encode('utf-8'),objid.encode('utf-8'),valuename.encode('utf-8'),ct.byref(err))
    if err.value !=0:
        print('get_obj_value_smartmathis exited with code error: ',err.value)
        if err.value == 1 : print(objtype,' is unknown')
        if err.value == 2 : print(objid, ' is unknown')
        if err.value == 3 : print(valuename, ' is unknown')
    return objvalue

def get_obj_number(dll,objtype):
    """
    This function gets the total number of objects in mathis case
    :param dll: the opened smartmathis dll
    :param objtype: type of MATHIS object: 'LOC', 'BRANCH','BOUND','WALL','CTRL','HSRC','PERSON','SPEC' or 'CTRL'
    :return: integer format
    """
    dll.GIVE_OBJ_NUMBER_SMARTMATHIS.argtypes = [ct.c_char_p,ct.POINTER(ct.c_int)]
    dll.GIVE_OBJ_NUMBER_SMARTMATHIS.restype = ct.c_int
    err = ct.c_int(0)
    objvalue = dll.GIVE_OBJ_NUMBER_SMARTMATHIS(objtype.encode('utf-8'),ct.byref(err))
    if err.value != 0:
        print('get_obj_number_smartmathis exited with code error: ', err.value,' - ',objtype, ' is unknown')
    return objvalue

def write2file(file,header,kwargs):
    """
    This function is made to write the input data file needed for mathis. It's an internal function used in CreateObj()
    :param file: the opened object file
    :param header: the type of object concerned
    :param kwargs: list of attribute
    :return: none
    """
    line2write = '&'+header+' '
    for key, value in kwargs.items():
        if type(value) == str:
            line2write += " " + key + "='" + value +"'"
        elif type(value) == list:
            if type(value[0]) == str:
                line2write += " " + key + "='" + value[0] +"'"
                for val in value[1:]:
                    line2write += ",'"+val+"'"
            elif type(value[0]) == tuple:
                line2write = dealWithTuple(line2write,key,value)
            else:
                line2write += " " + key + "=" + str(value[0])
                for val in value[1:]:
                    line2write += ","+str(val)
        else:
            line2write += " " + key + "=" + str(value)
    line2write += '  /\n'
    file.write(line2write)
    return file

def dealWithTuple(line2write, key, value):
    line2write += ' \n'
    for idx,cpl in enumerate(value):
        for idxy,val in enumerate(cpl):
            line2write += key +'('+str(idx+1)+','+str(idxy+1)+') = '+str(val)+'  '
        line2write += ' \n'
    return line2write


def CreateFile(Path2Case,filename):
    """
    This function create and open the file for the *.data
    :param filename: name of the *.data file
    :return: none
    """
    if not os.path.isdir(Path2Case):
        os.mkdir(Path2Case)
    file = open(os.path.join(Path2Case,filename + '.data'), 'w')
    return file

def CreateObj(file,Type,**kwargs):
    """
    This function is used to create the corresponding object in the *.data
    :param file: opened file
    :param Type: the type of object to create
    :param kwargs: list of attribute for the object to be created
    :return: the .*data file is appended by the created object with its attributes
    """
    file = write2file(file, Type, kwargs)
    return file

if __name__ == '__main__':
    print('Mathis exchange function')