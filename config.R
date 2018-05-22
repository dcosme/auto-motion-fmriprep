# paths
#This is where all subject-numbered directories are:
confoundDir = '~/Documents/code/auto-motion-fmriprep/data/'
outputDir = '~/Documents/code/auto-motion-fmriprep/output'

# variables
study = 'TAG'
subPattern = 'sub-([0-9]{3})'
wavePattern = 'ses-wave([0-9]{1})'
taskPattern = 'task-(cyb|rest|stop|vid)'
runPattern = 'run-([0-9]{2})'
parallelize = TRUE
leave_n_free_cores = 0
