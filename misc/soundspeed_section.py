"""
Soundspeed section plot
"""
import matplotlib.pyplot as plt
import xarray as xr
import numpy as np
import gsw

from lo_tools import Lfun, zrfun
from lo_tools import plotting_functions as pfun

Ldir = Lfun.Lstart()
fn = (Ldir['parent'] / 'LiveOcean_roms' / 'output' /
    'cas6_v3_lo8b' / 'f2019.07.04' / 'ocean_his_0020.nc')
ds = xr.open_dataset(fn)
# create track by hand
x = np.linspace(-124.85,-124.2, 100) # shelf only
#x = np.linspace(-126,-124.2, 100) # shows SOFAR channel
y = 47 * np.ones(x.shape)
in_dict = {'fn': fn}
v2, v3, dist, idist0 = pfun.get_section(ds, 'salt', x, y, in_dict)
s = v3['sectvarf']
v2, v3, dist, idist0 = pfun.get_section(ds, 'temp', x, y, in_dict)
th = v3['sectvarf']

X = v3['distf']
Z = v3['zrf']
# adjust so surface is at 0
Z = Z - Z[-1,:]

p = gsw.p_from_z(Z, 47)
SA = gsw.SA_from_SP(s, p, -125, 47)
CT = gsw.CT_from_pt(SA, th)
spd = gsw.sound_speed(SA, CT, p)


# PLOTTING
plt.close('all')

# START
fs = 14
pfun.start_plot(fs=fs, figsize=(16,9))
fig, axes = plt.subplots(nrows=3, ncols=2)

ax = axes[0,0]
cs = ax.pcolormesh(X, Z, SA, cmap='jet')
fig.colorbar(cs, ax=ax)
ax.text(.95, .05, 'Absolute Salinity', transform=ax.transAxes, ha='right')

ax = axes[1,0]
cs = ax.pcolormesh(X, Z, CT, cmap='jet')
fig.colorbar(cs, ax=ax)
ax.text(.95, .05, 'Conservative Temperature', transform=ax.transAxes, ha='right')

ax = axes[2,0]
cs = ax.pcolormesh(X, Z, spd, cmap='jet')
fig.colorbar(cs, ax=ax)
ax.text(.95, .05, 'Soundspeed [m/s]', transform=ax.transAxes, ha='right')

ax = axes[0,1]
ax.plot(SA,Z, alpha=.2)
ax.text(.05, .05, 'Absolute Salinity', transform=ax.transAxes, ha='left')

ax = axes[1,1]
ax.plot(CT,Z, alpha=.2)
ax.text(.95, .05, 'Conservative Temperature', transform=ax.transAxes, ha='right')

ax = axes[2,1]
ax.plot(spd,Z, alpha=.2)
ax.text(.95, .05, 'Soundspeed [m/s]', transform=ax.transAxes, ha='right')

fig.suptitle(str(fn))

plt.show()
pfun.end_plot()


