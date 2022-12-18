"""
A snippet of code to use as a template when running multiple
subprocesses at the same time.

Not functional on its own.
"""
from time import time
from subprocess import Popen as Po
from subprocess import PIPE as Pi
import sys

# Nproc controls how many subprocesses we allow to stack up
# before we require them all to finish.
Nproc = Ldir['Nproc']

proc_list = []
N = len(fn_list)
print('Times to extract =  %d' % (N))
tt0 = time()
for ii in range(N):
    # Need to form a command as a list "cmd_list"
    proc = Po(cmd_list, stdout=Pi, stderr=Pi)
    proc_list.append(proc)
    # run a collection of processes
    if ((np.mod(ii,Nproc) == 0) and (ii > 0)) or (ii == N-1):
        for proc in proc_list:
            proc.communicate() # make sure all are finished
        proc_list = []
print(' - time for processing %0.2f sec' % (time()-tt0))