"""
One-off code to remove a bunch of puckets from kopah.
"""

from subprocess import Popen as Po
from subprocess import PIPE as Pi
import sys
import pandas as pd
from datetime import datetime, timedelta

dti = pd.date_range(datetime(2024,11,27), datetime(2025,5,3))

def messages(mess_str, stdout, stderr):
    # utility function to help with subprocess errors
    # try:
    #     if len(stdout) > 0:
    #         print(mess_str)
    #         print(stdout.decode())
    # except TypeError:
    #     pass
    try:
        if len(stderr) > 0:
            print(mess_str)
            print(stderr.decode())
    except TypeError:
        pass

for dt in dti:
    dstr = dt.strftime('%Y.%m.%d')
    cmd_list = ['s3cmd', 'rb', 's3://f'+dstr, '--force', '--recursive']
    print('\n'+dstr)
    proc = Po(cmd_list, stdout=Pi, stderr=Pi)
    stdout, stderr = proc.communicate()
    messages('s3cmd messages:', stdout, stderr)
    sys.stdout.flush()