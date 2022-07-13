"""
Code to test the PyCO2SYS module.

Info on useage and units is available here:
https://pyco2sys.readthedocs.io/en/latest/co2sys_nd/

This test is mainly to compare two versions of calling the program,
to make sure I understand the parameters we are passing.
"""

# My current useage
from PyCO2SYS import CO2SYS
salt = 35
temp = 20 # deg C
DIC = 2000 # umol kg-1
Alk = 2300 # ueq kg-1
pres = 0 # dbar
r1 = CO2SYS(Alk, DIC, 1, 2, salt, temp, temp,
    pres, pres, 50, 2, 1, 10, 1, NH3=0.0, H2S=0.0)
"""
CO2SYS(PAR1, PAR2, PAR1TYPE, PAR2TYPE, SAL, TEMPIN, TEMPOUT, PRESIN, PRESOUT,
    SI, PO4, pHSCALEIN, K1K2CONSTANTS, KSO4CONSTANTS, NH3=0.0, H2S=0.0, KFCONSTANT=1,       opt_buffers_mode=1, totals=None, equilibria_in=None, equilibria_out=None, WhichR=1)
    
NOTE that the "in" and "out" versions of the returned variables will be
identical because we pass the same pressure and temperature for
input and output.

So it appears we are using:
    SI = 50
    PO4 = 2
    pHSCALEIN = 1
    K1K2CONSTANTS = 10
    KSO4CONSTANTS = 1
"""

# New useage as suggested by the docs.
import PyCO2SYS as pyco2
r2 = pyco2.sys(par1=Alk, par2=DIC, par1_type=1, par2_type=2,
    salinity=salt, temperature=temp, pressure=pres,
    total_silicate=50, total_phosphate=2,
    opt_pH_scale=1, opt_k_carbonic=10, opt_k_bisulfate=1)

# compare results
print('r1: pH=%0.5f OmAr=%0.5f' % (r1['pHout'],r1['OmegaARout']))
print('r2: pH=%0.5f OmAr=%0.5f' % (r2['pH'],r2['saturation_aragonite']))
"""
RESULT: these are identical, and I prefer the second usage because it has
more explicit use of kwargs.

Note that in both cases pH and pH_total are identical.
"""

