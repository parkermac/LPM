"""
Code to compare observed and modeled SSH time series at tide stations.
"""

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import pandas as pd
import utide
from lo_tools import Lfun, zfun
from lo_tools import plotting_functions as pfun

Ldir = Lfun.Lstart()

gtagex = 'cas7_t0_x4b'
year_str = '2022'
mod_fn = Ldir['LOo'] / 'extract' / gtagex / 'tide' / ('ssh_df_' + year_str + '.p')
sn_fn = Ldir['LOo'] / 'extract' / gtagex / 'tide' / ('sn_df_' + year_str + '.p')
obs_dir = Ldir['LOo'] / 'obs' / 'tide'

#
mod_df = pd.read_pickle(mod_fn)
sn_df = pd.read_pickle(sn_fn)

# Combine all the observed Series into a single DataFrame in the same format
# as the model extractions.
obs_df = pd.DataFrame(index = mod_df.index, columns = mod_df.columns)
for sn in mod_df.columns:
    if sn[0] == '0':
        source = 'dfo'
    else:
        source = 'noaa'
    fn = obs_dir / ('tide_' + source + '_' + str(sn) + '_' + year_str + '.p')
    ser = pd.read_pickle(fn)
    obs_df.loc[:,sn] = ser

# remove means
obs_df -= obs_df.mean()
mod_df -= mod_df.mean()

# harmonic analysis
def get_harmonics(ser, lat):
    t = ser.index
    z = ser.to_numpy(dtype=float)
    h = utide.solve(t, z, v=None,
                 lat=lat,
                 nodal=False,
                 trend=False,
                 method='ols',
                 conf_int='linear',
                 Rayleigh_min=0.95)
    # h.aux.freq has units cyles/hour
    # so for f = h.aux.frq[h.name == 'M2'][0] we get
    # 1/f = 12.420601202671868 (hours per cycle)
    # h.A is amplitude (m), h.g is phase (degrees)
    return h

def get_AG(hn, Hobs, Hmod):
    #convenience function for loading constituent info
    ho = Hobs
    hm = Hmod
    # we use the "[0]" because these are arrays and we want floats
    Ao = ho.A[ho.name==hn][0]
    Am = hm.A[hm.name==hn][0]
    Go = ho.g[ho.name==hn][0]
    Gm = hm.g[hm.name==hn][0]
    Fo = 24*ho.aux.frq[ho.name==hn][0] # cycles per day
    Fm = 24*hm.aux.frq[hm.name==hn][0]
    # fix when phase difference straddles 360
    if (Gm - Go) > 180:
        Gm = Gm - 360
    elif (Gm - Go) < -180:
        Gm = Gm + 360
    else:
        pass
    return Ao, Am, Go, Gm, Fo, Fm

# list of frequencies to consider.  Sometimes we want to limit this
# because for shorter records utide can't separate nearby peaks
#hn_list = ['M2','S2','N2','O1','P1','K1']
hn_list = ['M2','S2','N2','O1','K1']

plt.close('all')

# look at things
for sn in sn_df.index:
    lat = sn_df.loc[sn,'lat']
    mod_ser = mod_df[sn]
    obs_ser = obs_df[sn]

    Hmod = get_harmonics(mod_ser, lat)
    Hobs = get_harmonics(obs_ser, lat)

    for hn in hn_list:
        Ao, Am, Go, Gm, Fo, Fm = get_AG(hn, Hobs, Hmod)
        print('%s: Ao=%0.3f Am=%0.3f Go=%0.1f Gm=%0.1f Fo=%0.3f Fm=%0.3f ' % (hn, Ao, Am, Go, Gm, Fo, Fm))

    # plotting
    pfun.start_plot(figsize=(15,8))
    fig = plt.figure()
    ax = fig.add_subplot(111)
    mod_df[sn].plot(ax=ax)
    obs_df[sn].plot(ax=ax)
    ax.set_title(sn_df.loc[sn,'name'])
    plt.show()