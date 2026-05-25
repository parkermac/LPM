"""
Code to run the job array code.

This should be run on klone, first invoking
pmsrun2
conda activate loenv
python3 driver.py
"""

from subprocess import Popen as Po
from subprocess import PIPE as Pi
from time import time

from lo_tools import Lfun
Ldir = Lfun.Lstart()

out_dir = Ldir['parent'] / 'LPM_output' / 'job_array_test'
Lfun.make_dir(out_dir, clean=True)

tt0 = time()

# launch the job arrays using sbatch, as a subprocess
njobs = 30
cmd_list = ['sbatch','--array=1-' + str(njobs),
    'sbatch_worker.sh','cas7_t2_x11b','2025.01.01','hourly']
proc = Po(cmd_list, stdout=Pi, stderr=Pi)
stdout, stderr = proc.communicate()

print('time for all jobs %0.1f sec' % (time()-tt0))