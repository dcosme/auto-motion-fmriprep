#!/bin/bash
#
#SBATCH --job-name=auto-motion-fmriprep
#SBATCH --output=auto-motion-fmriprep.log
#SBATCH --cpus-per-task=1
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=1G
#SBATCH --partition=short,fat,long,longfat

module load R gcc

Rscript --verbose auto_motion_fmriprep.R
