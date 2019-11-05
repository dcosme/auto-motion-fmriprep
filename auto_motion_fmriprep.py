#!/usr/bin/env python3

import argparse
import sys
from confounds_file_reader import ConfoundsFileReader
from classifier import Classifier
import numpy
import numpy.lib.recfunctions
from pathlib import Path
from summarize import Summarize
from realignment import Realignment
from plotter import Plotter
from identifier import Identifier


def cli():
    """
    Define and parse command line arguments
    """

    prog_descrip = 'Auto-motion fmriprep'

    parser = argparse.ArgumentParser(description=prog_descrip,
                                     add_help=False,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-b', '--bids', metavar='BIDS Dir', action='store', required=True,
                        help='absolute path to your top level bids folder.',
                        dest='bids_dir'
                        )
    parser.add_argument('-s', '--study', metavar='Study Name', action='store', type=str, required=True,
                        help='Study name.',
                        dest='study'
                        )
    parser.add_argument('-l', '--level', action='store', required=True, type=str,
                        help='Level of the classification that will be performed.',
                        choices=['train', 'test'],
                        dest='level'
                        )
    parser.add_argument('-ne', '--no-euc', action='store_true', required=False, default=False,
                        help=('Do NOT use euclidean distance. Uses RAW realignment \
                            parameters instead. This arg SUPPRESSES euclidean distance \
                            for realignment parameters.'),
                        dest='noeuc'
                        )
    parser.add_argument('-nr', '--no-rp', action='store_true', required=False, default=False,
                        help='No rp_txt files. This arg SUPPRESSES file write.',
                        dest='norp'
                        )
    parser.add_argument('-p', '--plot', action='append', type=str,
                        required=False, default=None,
                        help='Space separated list of confounds to plot',
                        dest='plot_confounds',
                        choices=['csf',
                                 'white_matter',
                                 'global_signal',
                                 'std_dvars',
                                 'dvars',
                                 'framewise_displacement',
                                 'trans_x',
                                 'trans_y',
                                 'trans_z',
                                 'rot_x',
                                 'rot_y',
                                 'rot_z'])
    parser.add_argument('-f', '--fig-format', metavar='Fig File Format', action='store', type=str,
                        required=False, default='png',
                        help='file format for plot.',
                        dest='f_format'
                        )
    parser.add_argument('-h', '--fig-height', metavar='Fig Height', action='store', type=float,
                        required=False, default=5.5,
                        help='plot height in inches.',
                        dest='f_height'
                        )
    parser.add_argument('-w', '--fig-width', metavar='Fig Width', action='store', type=float,
                        required=False, default=7.0,
                        help='plot width in inches.',
                        dest='f_width'
                        )
    parser.add_argument('-dpi', '--fig-dpi', metavar='Fig DPI', action='store', type=int,
                        required=False, default=250,
                        help='plot resolution in dots per inch.',
                        dest='f_dpi'
                        )

    args = parser.parse_args()

    return args


def make_plots(identifier: Identifier, data: numpy.ndarray, artifact: numpy.ndarray, args: argparse.Namespace):
    if args.plot_confounds:
        plot_dir = Path(args.bids_dir, 'derivatives', 'auto-motion', 'plots')

        data_to_plot = numpy.lib.recfunctions.append_fields(data, 'artifact', artifact)
        plotter = Plotter(output_dir=plot_dir, identifier=identifier, data=data_to_plot,
                          height=args.f_height, width=args.f_width, dpi=args.f_dpi, format=args.f_format)
        for confound in args.plot_confounds:
            plotter.plot(column_name=confound)


def remove_field_name(a, name):
    names = list(a.dtype.names)
    if name in names:
        names.remove(name)
    b = numpy.lib.recfunctions.structured_to_unstructured(a[names], dtype=numpy.float32, copy=True)
    return b


def main():
    args = cli()

    # Get the training data and train the classifier
    c = ConfoundsFileReader(args.bids_dir)
    data = c.get_training_data()
    classifier = Classifier(remove_field_name(data, 'artifact'), data['artifact'])
    classifier.train()

    summary_dir = Path(args.bids_dir, 'derivatives', 'auto-motion', 'summary')
    summaries = Summarize(summary_dir, args.study)

    realignment_parameters_dir = Path(args.bids_dir, 'derivatives', 'auto-motion', 'rp_txt')
    rp = Realignment(realignment_parameters_dir)

    # Get the confounds data per subject, and predict motion artifacts
    for identifier, data in c.get_confounds():
        d = numpy.lib.recfunctions.structured_to_unstructured(data)
        artifact = classifier.predict(d)

        summaries.add(identifier=identifier, artifact=artifact)
        if not args.norp:
            rp.write(identifier=identifier, no_euclidean=args.noeuc, data=data, artifact=artifact)
        make_plots(identifier=identifier, data=data, artifact=artifact, args=args)

    summaries.write()


if __name__ == "__main__":
    sys.exit(main())
