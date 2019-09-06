# This script specifies the following user inputs for auto_motion_fmriprep.R:
# * confoundDir = path to the fmriprep confounds files
# * summaryDir = path to the output directory for summary csv files
# * rpDir = path to output directory to write new rp_txt files
# * plotDir = path to output directory to write plots
# * study = study name
# * subPattern = regular expression to extract subject ID
# * wavePattern = regular expression to extract wave number
# * taskPattern = regular expression to extract task name
# * runPattern = regular expression to extract run number
# * writeRP = whether to write out new rp_txt files; use TRUE or FALSE
# * writePlots = whether to write plots for each subject; use TRUE or FALSE
# * writeEuclidean = whether to use Euclidean distance instead of the raw realigment parameters
#   when exporting rp_txt files; use TRUE or FALSE. If TRUE, rp_txt files will incude the following columns:
#   Euclidean distance translation, Euclidean distance rotation, Euclidean distance derivative translation, 
#   Euclidean distance derivative rotation, trash. If FALSE, rp_txt files will incude the following columns: 
#   X, Y, Z, RotX, RotY RotZ, trash.
# * figIndicators = motion indicators to print in plot
# * figFormat = file format for plot
# * figHeight = plot height in inches
# * figWidth = plot width in inches
# * figDPI = plot resolution in dots per inch

# paths
confoundDir = '/projects/dsnlab/shared/tag/bids_data/derivatives/fmriprep'
summaryDir = '/projects/dsnlab/shared/tag/TAG_scripts/fMRI/fx/motion/auto-motion-fmriprep/summary'
plotDir = '/projects/dsnlab/shared/tag/TAG_scripts/fMRI/fx/motion/auto-motion-fmriprep/plots'
rpDir = '/projects/dsnlab/shared/tag/TAG_scripts/fMRI/fx/motion/auto-motion-fmriprep/rp_txt'

# variables
# please note the expected BIDS file pattern is e.g. sub-[TAG001]_ses-[wave1]_task-[DSD]_run-[01]_bold_confounds.tsv
# if you do not include the 'run' argument, you may need to modify the filePattern definition in lines 38 and 56 of auto_motion_fmriprep.R
study = 'TAG'
subPattern = 'sub-(.*[0-9]{3})'
wavePattern = 'ses-wave([0-9]{1})' # just extract the number
taskPattern = 'task-(SVC|DSD)'
runPattern = 'run-([0-9]{2})'
writeRP = TRUE
writePlot = TRUE
writeEuclidean = TRUE
figIndicators = c('FramewiseDisplacement', 'GlobalSignal', 'stdDVARS')
figFormat = '.png'
figHeight = 5.5
figWidth = 7
figDPI = 250
