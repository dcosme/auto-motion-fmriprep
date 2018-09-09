#!/bin/bash
#
#SBATCH --job-name=auto-motion-fmriprep
#SBATCH --output=auto-motion-fmriprep.log
#SBATCH --cpus-per-task=28
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=1000
#SBATCH --partition=defq,short,fat,long,longfat

module load R gcc

srun Rscript --verbose auto_motion_fmriprep.R
