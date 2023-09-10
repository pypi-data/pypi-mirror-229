"""
Versions: 1.7.7
Date: 2022.12.20
Author: Mart.Hanks
Description:
The library is designed for HIL/SIL automation test
HIL is Hardware in the loop
SIL is Software in the loop
"""

import win32api
import win32con
try:
    import clr
    import System
except Exception as e:
    print('clr, System lib can not be import...\n' + str(e))


# Load ASAM assemblies from the global assembly cache (GAC)
__global_dll = win32api.RegOpenKey(win32con.HKEY_CLASSES_ROOT,
                                 r'Installer\Assemblies\Global',
                                 0,
                                 win32con.KEY_READ)

__dll_id = 0
__XIL_Interfaces = []
__XIL_Implementation_TestbenchFactory = []
__EESPort_Interfaces_Extended = []
__XIL_Interfaces_str = 'ASAM.XIL.Interfaces,'
__XIL_Implementation_TestbenchFactory_str = 'ASAM.XIL.Implementation.TestbenchFactory,'
__EESPort_Interfaces_Extended_str = 'dSPACE.XIL.Testbench.EESPort.Interfaces.Extended,'
while True:
    try:
        __dll_info = win32api.RegEnumValue(__global_dll, __dll_id)
        if __XIL_Interfaces_str in __dll_info[0]:
            __XIL_Interfaces.append(__dll_info[0])
            __dll_id += 1
            continue
        if __XIL_Implementation_TestbenchFactory_str in __dll_info[0]:
            __XIL_Implementation_TestbenchFactory.append(__dll_info[0])
            __dll_id += 1
            continue
        if __EESPort_Interfaces_Extended_str in __dll_info[0]:
            __EESPort_Interfaces_Extended.append(__dll_info[0])
            __dll_id += 1
            continue
        __dll_id += 1
    except:
        break

win32api.RegCloseKey(__global_dll)

def __getHighVersion(assemblyString_l):
    result = ''
    assemblyString_l_num = len(assemblyString_l)
    if assemblyString_l_num == 0:
        return 'No Such Dll'
    if assemblyString_l_num == 1:
        result = assemblyString_l[0]
    else:
        v_l = []
        for item in assemblyString_l:
            item_l = item.split(',')
            for seg in item_l:
                if 'VERSION' in seg.upper() and 'FILEVERSION' not in seg.upper():
                    raw_v = seg.split('=')[1]
                    raw_v = raw_v.replace('"', '').replace('.', '')
                    raw_v = '1.' + raw_v
                    v_l.append(float(raw_v))
                    break
        #find newest version
        i = v_l.index(max(v_l))
        result = assemblyString_l[i]
    return result

__assemblyString_a = __getHighVersion(__XIL_Interfaces)
__assemblyString_b = __getHighVersion(__XIL_Implementation_TestbenchFactory)
__assemblyString_c = __getHighVersion(__EESPort_Interfaces_Extended)

try:
    clr.AddReference(__assemblyString_a)
except Exception as e:
    print('ASAM.XIL.Interfaces assemblies was not be found...\n' + str(e))

try:
    clr.AddReference(__assemblyString_b)
except Exception as e:
    print('ASAM.XIL.Implementation.TestbenchFactory assemblies was not be found...\n' + str(e))   

try:
    clr.AddReference(__assemblyString_c)
except Exception as e:
    print('dSPACE.XIL.Testbench.EESPort.Interfaces.Extended assemblies was not be found...\n' + str(e))

try:
    # Import XIL API .NET classes from the .NET assemblies
    import ASAM.XIL.Implementation.TestbenchFactory.Testbench
    import ASAM.XIL.Interfaces.Testbench
    import ASAM.XIL.Interfaces.Testbench.MAPort
    from ASAM.XIL.Interfaces.Testbench.Common import Error, ValueContainer
    from ASAM.XIL.Implementation.TestbenchFactory.Testbench import TestbenchFactory
    from ASAM.XIL.Interfaces.Testbench.EESPort.Error import EESPortException
    from ASAM.XIL.Interfaces.Testbench.EESPort.Enum import EESPortState, ErrorCategory, ErrorType, LoadType, TriggerType
    from ASAM.XIL.Interfaces.Testbench.EESPort import IEESPortConfig
    from dSPACE.XIL.Testbench.EESPort.Interfaces.Extended import IDSEESPort, IDSErrorSet, IDSEESPortConfig
except Exception as e:
    print('dSPACE XIL API .NET was not be found or its version is not supported...\n' + str(e))

if __name__ == '__main__':
    print('This is the auxil library...')

