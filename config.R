# paths
#This is where all subject-numbered directories are:
confoundDir = '~/Documents/code/auto-motion-fmriprep/data/'
outputDir = '~/Documents/code/auto-motion-fmriprep/output'
plotDir = '~/Documents/code/auto-motion-fmriprep/plots/'
rpDir = '~/Documents/code/auto-motion-fmriprep/rp_txt/'

# variables
study = 'TAG|TDS'
subPattern = 'sub-(.*[0-9]{3})'
wavePattern = 'ses-wave([0-9]{1})'
taskPattern = 'task-(SVC|DSD|cyb|stop|vid)'
runPattern = 'run-([0-9]{2})'
parallelize = TRUE
leave_n_free_cores = 0
writeRP = TRUE
