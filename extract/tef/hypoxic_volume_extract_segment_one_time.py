"""
This code extracts all needed hypoxic volume segment data for one history file,
looping over all segments.

"""
from pathlib import Path
import sys
import argparse
import numpy as np
import xarray as xr
from time import time
import pickle
import pandas as pd

from lo_tools import Lfun, zfun, zrfun

# command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('-pth', type=str) # path to LO_roms
parser.add_argument('-out_dir', type=str) # path to temporary directory for output
parser.add_argument('-gtagex', type=str) # gtagex
parser.add_argument('-d', type=str) # date string like 2019.07.04
parser.add_argument('-nhis', type=int, default=1) # history file number, 1-25
parser.add_argument('-testing', type=Lfun.boolean_string, default=False)
args = parser.parse_args()

Ldir = Lfun.Lstart(gridname=args.gtagex.split('_')[0])

pth = Ldir['LO'] / 'extract' / 'tef'
if str(pth) not in sys.path:
    sys.path.append(str(pth))
import tef_fun

nhiss = ('0000' + str(args.nhis))[-4:]
fn = Path(args.pth) / args.gtagex / ('f' + args.d) / ('ocean_his_' + nhiss + '.nc')
out_dir = Path(args.out_dir)
Lfun.make_dir(out_dir)
out_fn  = out_dir / ('A_' + args.d + '_' + nhiss + '.p')
out_fn.unlink(missing_ok=True)

# ---
# get grid info
G, S, T = zrfun.get_basic_info(fn)
h = G['h']
DA = G['DX'] * G['DY']
DA3 = DA.reshape((1,G['M'],G['L']))

# get segment info
vol_dir = Ldir['LOo'] / 'extract' / 'tef' / ('volumes_' + Ldir['gridname'])
v_df = pd.read_pickle(vol_dir / 'volumes.p')
j_dict = pickle.load(open(vol_dir / 'j_dict.p', 'rb'))
i_dict = pickle.load(open(vol_dir / 'i_dict.p', 'rb'))
seg_list = list(v_df.index)

# set list of variables to extract
vn_list = ['oxygen']

tt0 = time()
print(fn)
    
ds = xr.open_dataset(fn)

vn_dict = {}
for vn in vn_list:
    vn_dict[vn] = ds[vn][0,:,:,:].values
zeta = ds['zeta'][0,:,:].values
ds.close()

# find the hypoxic volume and other variables for each segment, at this time
A = pd.DataFrame(index=seg_list)
AA = dict()
for seg_name in seg_list:
    
    jjj = j_dict[seg_name]
    iii = i_dict[seg_name]
    z_w = zrfun.get_z(h[jjj,iii], zeta[jjj,iii], S, only_w=True)
    dz = np.diff(z_w, axis=0)
    DV = dz * DA3[0,jjj,iii]
    volume = DV.sum()
    AA['volume'] = volume
    
    mask = vn_dict['oxygen'][:,jjj,iii] > 31.25
    DV_hvol = DV.copy()
    DV_hvol[mask] = 0
    AA['hypoxic_volume_1'] = DV_hvol.sum()
    
    mask = vn_dict['oxygen'][:,jjj,iii] > 62.5
    DV_hvol = DV.copy()
    DV_hvol[mask] = 0
    AA['hypoxic_volume_2'] = DV_hvol.sum()
    
    mask = vn_dict['oxygen'][:,jjj,iii] > 93.75
    DV_hvol = DV.copy()
    DV_hvol[mask] = 0
    AA['hypoxic_volume_3'] = DV_hvol.sum()
    
    for vn in vn_list:
        AA[vn] = (vn_dict[vn][:,jjj,iii] * DV).sum()/volume
            
    # store results
    for vn in vn_list + ['volume', 'hypoxic_volume_1', 'hypoxic_volume_2', 'hypoxic_volume_3']:
        A.loc[seg_name, vn] = AA[vn]
            
print('  ** took %0.1f sec' % (time()-tt0))
sys.stdout.flush()

A.to_pickle(out_fn)
print('Time to extract all segment data = %0.2f sec' % (time()-tt0))
sys.stdout.flush()

