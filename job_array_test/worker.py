"""
Worker code that is called as a member of the job array.
"""

from datetime import datetime
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-tid', type=str)
parser.add_argument('-in_dir', type=str)
parser.add_argument('-out_dir', type=str)
args = parser.parse_args()

time_format = '%Y.%m.%d %H:%M:%S'
time_str = datetime.now().strftime(time_format)

out_fn = args.out_dir + '/' + args.tid + '.txt'
with open(out_fn, 'w') as ffout:
    ffout.write(time_str)
