"""
An example of running multiple subprocesses at the same time.
"""
from time import time
from subprocess import Popen as Po
from subprocess import PIPE as Pi
import sys
import numpy as np

# Set the total number of times to run the job.
N = 100
print('Total number of jobs =  %d' % (N))

# Nproc controls how many subprocesses we allow to stack up
# at once before we require them all to finish.
Nproc = 100

# This is the command we will run.
cmd_list = ['sleep','5']

# Initialize an empty list of processes.
proc_list = []

# loop over all jobs
tt0 = time()
for ii in range(N):
    # Launch a job and add its process to a list.
    proc = Po(cmd_list, stdout=Pi, stderr=Pi)
    proc_list.append(proc)
    
    # If we have accumulated Nproc jobs, or are at the end of the
    # total number of jobs, then stop and make sure all the jobs
    # in proc_list have finished, using the communicate method.
    if ((np.mod(ii,Nproc) == 0) and (ii > 0)) or (ii == N-1):
        for proc in proc_list:
            stdout, stderr = proc.communicate()
            if len(stderr) > 0:
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