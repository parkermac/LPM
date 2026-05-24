# Code to run the job array code.
"""
This should be run on klone, first invoking
pmsrun2
conda activate loenv
"""

from subprocess import Popen as Po
from subprocess import PIPE as Pi
from time import time

from lo_tools import Lfun
Ldir = Lfun.Lstart()

out_dir = Ldir['parent'] / 'LPM_output' / 'job_array_test'
Lfun.make_dir(out_dir)

tt0 = time()

# launch the job arrays using sbatch, as a subprocess
# sbatch --array=1-192 ./sbatch_worker.sh
cmd_list = ['sbatch','--array=1-192',
    'sbatch_worker.sh']
proc = Po(cmd_list, stdout=Pi, stderr=Pi)
stdout, stderr = proc.communicate()