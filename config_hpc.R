# paths
#This is where all subject-numbered directories are:
homeDir = '/home/dcosme/auto-motion-fmriprep/'
confoundDir = '/home/dcosme/auto-motion-fmriprep/data/'
outputDir = '/home/dcosme/auto-motion-fmriprep/output'
plotDir = '/home/dcosme/auto-motion-fmriprep/plots/'
rpDir = '/home/dcosme/auto-motion-fmriprep/rp_txt/'

# variables
study = 'TAG|TDS'
subPattern = 'sub-(.*[0-9]{3})'
wavePattern = 'ses-wave([0-9]{1})'
taskPattern = 'task-(SVC|DSD|cyb|stop|vid)'
runPattern = 'run-([0-9]{2})'
parallelize = TRUE
leave_n_free_cores = 0
writeRP = TRUE
