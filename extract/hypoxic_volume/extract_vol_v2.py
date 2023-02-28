"""
Code to extract hypoxic volumes from LO domain.
Baesd code on extract/box and /tef2 code: extract_sections; extract_one_section
updated code to make the volume calculations run faster 

To test on mac:
run extract_vol_v2 -gtx cas6_v0_live -0 2021.07.03 -1 2022.07.06 -test True 

Need to add in testing lines 
2 history files, all hypoxia Total processing time = 2.71 sec 
Add Oag, Total processing time = 185.70 sec (b/c have to calc Oag for each layer whole domain)
File size 2 history files = ~103 MB 
os.stat(file).st_size
took 806.93 sec on perigee? 
Testing January 2023 - present
"""

# imports
from lo_tools import Lfun, zfun, zrfun
from lo_tools import extract_argfun as exfun
Ldir = exfun.intro() # this handles the argument passing

from subprocess import Popen as Po
from subprocess import PIPE as Pi

from time import time
import sys 
import pandas as pd
import xarray as xr
import numpy as np
import pickle

fn_list = Lfun.get_fn_list('daily', Ldir, Ldir['ds0'], Ldir['ds1'])

out_dir0 = Ldir['LOo'] / 'extract' / Ldir['gtagex'] / 'hypoxic_volume'
out_dir = out_dir0 / ('extractions_' + Ldir['ds0'] + '_' + Ldir['ds1'])
temp_dir = out_dir0 / ('temp_' + Ldir['ds0'] + '_' + Ldir['ds1'])
Lfun.make_dir(out_dir, clean=True)
Lfun.make_dir(temp_dir, clean=True)

print('...working on files')

# still working on this if section
if Ldir['testing']:
    fn_list = [fn_list[0]]

# loop over all jobs
tt0 = time()
N = len(fn_list)
proc_list = []
for ii in range(N):
    # Launch a job and add its process to a list.
    fn = fn_list[ii]
    ii_str = ('0000' + str(ii))[-5:]
    out_fn = temp_dir / ('CC_' + ii_str + '.nc')
    # use subprocesses
    cmd_list = ['python3', 'get_one_volume.py',
            '-lt','daily',
            '-in_fn',str(fn),
            '-out_fn', str(out_fn)]
    proc = Po(cmd_list, stdout=Pi, stderr=Pi)
    proc_list.append(proc)
    # If we have accumulated Nproc jobs, or are at the end of the
    # total number of jobs, then stop and make sure all the jobs
    # in proc_list have finished, using the communicate method.
    if ((np.mod(ii,Ldir['Nproc']) == 0) and (ii > 0)) or (ii == N-1):
        for proc in proc_list:
            stdout, stderr = proc.communicate()
            if len(stdout) > 0:
                print('\nSTDOUT:')
                print(stdout.decode())
                sys.stdout.flush()
            if len(stderr) > 0:
                print('\nSTDERR:')
                print(stderr.decode())
                sys.stdout.flush()
        # Then initialize a new list.
        proc_list = []
    # Print screen output about progress.
    if (np.mod(ii,10) == 0) and ii>0:
        print(str(ii), end=', ')
        sys.stdout.flush()
    if (np.mod(ii,50) == 0) and (ii > 0):
        print('') # line feed
        sys.stdout.flush()
    if (ii == N-1):
        print(str(ii))
        sys.stdout.flush()

print('Total processing time = %0.2f sec' % (time()-tt0))

if Ldir['testing'] == False:
    
    # concatenate the records into one file
    # This bit of code is a nice example of how to replicate a bash pipe
    pp1 = Po(['ls', str(temp_dir)], stdout=Pi)
    pp2 = Po(['grep','CC'], stdin=pp1.stdout, stdout=Pi)
    fn_p = 'Volumes_O2_Oag_'+str(Ldir['ds0'])+'_'+str(Ldir['ds1']+'.nc')
    temp_fn = str(temp_dir)+'/'+fn_p # this is all the maps put to one
    cmd_list = ['ncrcat','-p', str(temp_dir), '-O', temp_fn]
    proc = Po(cmd_list, stdin=pp2.stdout, stdout=Pi, stderr=Pi)
    stdout, stderr = proc.communicate()
    if len(stdout) > 0:
        print('\nSTDOUT:')
        print(stdout.decode())
        sys.stdout.flush()
    if len(stderr) > 0:
        print('\nSTDERR:')
        print(stderr.decode())
        sys.stdout.flush()
        
    ds1 = xr.open_dataset(temp_fn)
    this_fn = out_dir / (fn_p)
    ds1.to_netcdf(this_fn)