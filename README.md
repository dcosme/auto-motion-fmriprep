[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.1412131.svg)](https://doi.org/10.5281/zenodo.1412131)

# auto-motion-fmriprep
Performs automated assessment of motion artifacts in fMRI data using `fmriprep` confounds.

**If you use `fmriprep` and would like to contribute to this project by sharing your `confounds_regressors.tsv` files (and potentially hand coded visual artifacts), please email me!**

## About
auto-motion-fmriprep uses machine learning and the motion indicators from [`fmriprep`](https://github.com/poldracklab/fmriprep) to detect motion artifacts in fMRI data and returns an "artifact" regressor (i.e. a series of 1s and 0s denoting the presence or absence of motion artifacts) that can be used in first level models along with other nuisance regressors.

This paradigm was developed to accurately classify visual motion artifacts (i.e. striping) using data from the [Developmental Social Neuroscience Lab](https://github.com/dsnlab) at the University of Oregon. The classifier can be trained on new data, and applied to new data to predict motion artifacts using these scripts. For more information about the development and validation of the classifier, please check out my poster from [FLUX 2018](https://dcosme.github.io/posters/Cosme_FLUX_2018.pdf).

## Requirements
* fMRI data must be preprocessed using `fmriprep` and each sequence you want to model must have a `confounds_regressors.tsv` file
* [Python](www.python.org)

## Usage
To use from source, first add the path to `auto-motion-fmriprep` to PYTHONPATH
```
export PYTHONPATH=$PYTHONPATH:/path/to/auto-motion-fmriprep/src
```

Then run `auto-motion-fmriprep`, specifying where the BIDS are stored, the study name and where the training data is:
```
python3 auto-motion-fmriprep.py -b /bids_data -t /training_data -s STUDY
```
Output is written to each BIDS derivatives/auto-motion-fmriprep folder.

### Optional command line arguments
- `-nr` Suppress output of realignment parameters. Omitting this option means that realignment parameters will be written to a text file for each participant/wave/task/run.
- `-ne` Output raw realignment parameters. Omitting this option means that Euclidean distance realignment parameters will be written.
- `-p` Confound to plot, with markers indicating volumes with motion artifacts. This option can be repeated to create multiple figures.
- `-f` Figure file format, such as `png`, `jpg`, `pdf`. Supports file formats supported by [matplotlib](https://matplotlib.org/).
- `-h` Figure height in inches (default 5.5 inches)
- `-w` Figure width in inches (default 7.0 inches)
- `-dpi` Figure dpi (default 250)

If `-p` is specified with a confound name, it will export plots with volumes predicted to have motion artifacts highlighted. Here is an example plot using framewise displacement, global signal, and standardized DVARS:

![example plot](example_plot.png)

## Acknowledgements
Thank you to [John C. Flournoy](https://github.com/jflournoy) and [Nandita Vijayakumar](https://github.com/nandivij) for their help developing this code. Huge thank you to Gracie Arnone, Oscar Bernat, Cameron Hansen, Leticia Hayes, & Nathalie Verhoeven for helping hand code motion artifacts.
