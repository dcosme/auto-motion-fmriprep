# This script specifies the following user inputs for auto_motion_fmriprep.R:
# * confoundDir = path to the fmriprep confounds files
# * outputDir = path to output directory; will create a new folder called auto-motion-fmriprep here
# * study = study name
# * ses = include session; use TRUE if ses is part of the file name, use FALSE if not
# * oldfmriprep = use TRUE if using version 1.1.8 or earlier; FALSE if 1.1.2 or later
# * noRP = suppress motion regressor text files; use TRUE or FALSE
# * nonames = suppress motion regressor text file colum namess; use TRUE or FALSE
# * noPlots = suppress plots for each subject run; use TRUE or FALSE
# * noEuclidean = do not use the Euclidean distance; use the raw realigment parameters instead
#   when exporting motion regressors files; use TRUE or FALSE. If FALSE, motion regressors files will include the following columns:
#   Euclidean distance translation, Euclidean distance rotation, Euclidean distance derivative translation, 
#   Euclidean distance derivative rotation, trash. If TRUE, motion regressors files will include the following columns: 
#   X, Y, Z, RotX, RotY RotZ, trash.
# * figIndicators = motion indicators to print in plot
# * figFormat = file format for plot
# * figHeight = plot height in inches
# * figWidth = plot width in inches
# * figDPI = plot resolution in dots per inch

# paths
confoundDir = '/data00/projects/MURI/data/BIDS/derivatives'
outputDir = '/data00/projects/MURI/data/BIDS/derivatives'

# variables
study = 'MURI'
ses = FALSE
oldfmriprep = FALSE
noRP = FALSE
noNames = FALSE
noPlot = FALSE
noEuclidean = FALSE
figIndicators = c('FramewiseDisplacement', 'GlobalSignal', 'stdDVARS')
figFormat = '.png'
figHeight = 5.5
figWidth = 7
figDPI = 250
