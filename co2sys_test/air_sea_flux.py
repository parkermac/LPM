"""
Code to develop the calculation of air-sea CO2 flux.
"""

from lo_tools import Lfun, zrfun
from lo_tools import plotting_functions as pfun
import matplotlib.pyplot as plt
import xarray as xr
import PyCO2SYS as pyco2
import gsw
import numpy as np
from datetime import datetime, timedelta

Ldir = Lfun.Lstart()
dstr = '2017.07.04'
#dt = datetime.strptime(dstr, Lfun.ds_fmt)
fn = Ldir['roms_out'] / 'cas7_trapsV00_meV00' / ('f' + dstr) / 'ocean_his_0016.nc'
#fn = Ldir['roms_out'] / 'cas7_t0_x4b' / 'f2015.09.23' / 'ocean_his_0024.nc'

G, S, T = zrfun.get_basic_info(fn)
ds = xr.open_dataset(fn)
aa = pfun.get_aa(ds)
lon = G['lon_rho']
lat = G['lat_rho']
hh = G['h']
px, py = pfun.get_plon_plat(lon, lat)
v_dict = dict()
vn_in_list = ['temp', 'salt', 'alkalinity', 'TIC']

nlev = -1

zz = 0 * hh
for cvn in vn_in_list:
    v_dict[cvn] = ds[cvn][0,nlev,:,:].values.squeeze()
pres = gsw.p_from_z(zz, lat) # pressure [dbar]
SA = gsw.SA_from_SP(v_dict['salt'], pres, lon, lat)
CT = gsw.CT_from_pt(SA, v_dict['temp'])
rho = gsw.rho(SA, CT, pres) # in situ density
temp = gsw.t_from_CT(SA, CT, pres) # in situ temperature
# convert from umol/L to umol/kg using in situ dentity
alkalinity = 1000 * v_dict['alkalinity'] / rho
alkalinity[alkalinity < 100] = np.nan
TIC = 1000 * v_dict['TIC'] / rho
TIC[TIC < 100] = np.nan
# See LPM/co2sys_test/test0.py for info.
CO2dict = pyco2.sys(par1=alkalinity, par2=TIC, par1_type=1, par2_type=2,
    salinity=v_dict['salt'], temperature=temp, pressure=pres,
    total_silicate=50, total_phosphate=2,
    opt_pH_scale=1, opt_k_carbonic=10, opt_k_bisulfate=1)
ph = CO2dict['pH']
arag = CO2dict['saturation_aragonite']
pCO2 = CO2dict['pCO2']
#ds.close()

# Create pCO2atm using the same algorithm as in ROMS.
# This is documented in LPM/misc/pco2air_secular.
def get_pco2air(dt):
    """
    Input is a dateimte object
    Output is pCO2amt [units?] for that day.
    """
    import pandas as pd
    t = pd.Timestamp(dt)
    pi2 = 6.2831853071796
    D0 = 282.6; D1 = 0.125; D2 =-7.18; D3 = 0.86
    D4 =-0.99; D5 = 0.28; D6 =-0.80; D7 = 0.06
    dti = pd.date_range(start='1951-01-01', end='2030-12-31', freq='D')
    pmonth = t.year - 1951.0 + t.dayofyear/365.0
    pCO2air_secular = D0 + D1*pmonth*12.0 + D2*np.sin(pi2*pmonth+D3) + \
    D4*np.sin(pi2*pmonth+D5) + D6*np.sin(pi2*pmonth+D7)
    return pCO2air_secular
pCO2air = get_pco2air(T['dt'])
print('pCO2air = %0.2f' % (pCO2air))

# plotting
plt.close('all')
pfun.start_plot(figsize=(8,10))
fig = plt.figure()
ax = fig.add_subplot(111)

pCO2m = pfun.mask_edges(pCO2, lon, lat)
cs = ax.pcolormesh(px,py,pCO2m,vmin=300,vmax=1000,cmap='Spectral_r')
fig.colorbar(cs, ax=ax)

pfun.dar(ax)
pfun.add_coast(ax)
ax.axis(aa)
pfun.add_info(ax,fn)

ax.set_title('$pCO_{2SW}\ [\mu atm]$')

plt.show()
pfun.end_plot()


