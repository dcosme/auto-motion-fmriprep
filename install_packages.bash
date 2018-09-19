#!/bin/bash
#
#SBATCH --job-name=install_packages
#SBATCH --output=install_packages.log
#
#SBATCH --cpus-per-task=1
#SBATCH --ntasks=1
#SBATCH --mem-per-cpu=1000
#SBATCH --partition=defq,fat,long,longfat

module load R gcc

Rscript --verbose -e "osuRepo = 'http://ftp.osuosl.org/pub/cran/'; if(!require(tidyverse)){ install.packages('tidyverse',repos=osuRepo) }; if(!require(caret)){ install.packages('caret',repos=osuRepo) }; message('Installation complete')"
