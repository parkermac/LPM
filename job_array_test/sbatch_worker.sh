#!/bin/bash

## run as
# sbatch --array=1-192 ./sbatch_worker.sh

## Group
#SBATCH -A macc

## Node type
#SBATCH -p cpu-g2

## Number of nodes
#SBATCH --nodes=1

## Tasks per node (set to 1 so each job in the job array uses 1)
#SBATCH --ntasks-per-node=1

## Walltime 
#SBATCH --time=00:10:00

## Set memory use. Each slice (32 cores) has 256G, so there is about
## 8G available for each of the 192 cores.
#SBATCH --mem=4G

## Do not return until the job is finished. This allows the wrapper script,
## driver.py to do the next step after all of the jobs in the array have
## finished.
#SBATCH --wait

source /gscratch/macc/parker/miniconda3/etc/profile.d/conda.sh
conda activate loenv

# Paths (strings)
dir0='/gscratch/macc/parker'
in_dir=${dir0}'/LPM/job_array_test'
out_dir=${dir0}'/LPM_output/job_array_test'

# Run the workers
python3 ${in_dir}/worker.py -tid $SLURM_ARRAY_TASK_ID -in_dir ${in_dir} -out_dir ${out_dir} > ${out_dir}"/test_"$SLURM_ARRAY_TASK_ID".log"