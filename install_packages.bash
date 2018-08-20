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

Rscript --verbose -e "osuRepo = 'http://ftp.osuosl.org/pub/cran/'; if(!require(tidyverse)){ install.packages('tidyverse',repos=osuRepo) }; if(!require(caret)){ install.packages('caret',repos=osuRepo) }; if(!require(caTools)){ install.packages('caTools',repos=osuRepo) }; if(!require(reshape2)){ install.packages('reshape2',repos=osuRepo) }; if(!require(PRROC)){ install.packages('PRROC',repos=osuRepo) }; if(!require(purrr)){ install.packages('purrr',repos=osuRepo) }; if(!require(pROC)){ install.packages('pROC',repos=osuRepo) }; if(!require(doParallel)){ install.packages('doParallel',repos=osuRepo) }; message('Installation complete')"
