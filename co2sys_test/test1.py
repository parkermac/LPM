"""
Code to test the PyCO2SYS module.

Info on useage and units is available here:
https://pyco2sys.readthedocs.io/en/latest/co2sys_nd/

This test is to explore how the carbonate chemistry under different
perturbations.
"""

import PyCO2SYS as pyco2

if False:
    salt = 35
    temp = 20 # deg C
    DIC = 2000 # umol kg-1
    Alk = 2300 # ueq kg-1
    pres = 0 # dbar
else:
    # like shallow water off Hoodsport
    salt = 25
    temp = 10 # deg C
    DIC = 2100 # umol kg-1
    Alk = 2050 # ueq kg-1
    pres = 0 # dbar
    # like deep water off Hoodsport
    # salt = 31
    # temp = 10 # deg C
    # DIC = 2250 # umol kg-1
    # Alk = 2250 # ueq kg-1
    # pres = 100 # dbar

# get initial fCO2
r = pyco2.sys(par1=Alk, par2=DIC, par1_type=1, par2_type=2,
    salinity=salt, temperature=temp, pressure=pres,
    total_silicate=50, total_phosphate=2,
    opt_pH_scale=1, opt_k_carbonic=10, opt_k_bisulfate=1)
print('pH=%0.3f, CO2=%0.1f, HCO3=%0.1f, CO3=%0.1f, fCO2=%0.1f, DIC=%0.1f, Alk=%0.1f' %
  (r['pH'],r['CO2'],r['HCO3'],r['CO3'],r['fCO2'],r['dic'],r['alkalinity']))
fCO2_init = r['fCO2'].copy()

# loop over increasing DIC until we hit a specified fCO2 increase
fCO2 = fCO2_init
while fCO2 <= fCO2_init + 20:
    DIC += .1
    r = pyco2.sys(par1=Alk, par2=DIC, par1_type=1, par2_type=2,
        salinity=salt, temperature=temp, pressure=pres,
        total_silicate=50, total_phosphate=2,
        opt_pH_scale=1, opt_k_carbonic=10, opt_k_bisulfate=1)
    fCO2 = r['fCO2'].copy()
    print('pH=%0.3f, CO2=%0.1f, HCO3=%0.1f, CO3=%0.1f, fCO2=%0.1f, DIC=%0.1f, Alk=%0.1f' %
      (r['pH'],r['CO2'],r['HCO3'],r['CO3'],r['fCO2'],r['dic'],r['alkalinity']))
    


