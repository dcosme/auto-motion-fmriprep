#!/usr/bin/env python
#
""" Step one wraper for auto motion fmriprep project. 
    The initial script wraps user arguments and passes
    them to the current R script. This step can then be
    used to pass these arguments directly to a python
    function once it's written. 

Args:
    bids_dir (abspath): Full path to bids dir. Builds 
        to fmriprep dir.
    out_dir (abspath): Optional output dir. Builds to
        summary csv, rp_txt, and plot dirs. If not
        supplied, will be made in "auto_motion_output"
        dir in main script directory. 
    study (string): study name
    sub_reg (string): regular expression to extract subject ID
    wavePattern (string): regular expression to extract wave number
    taskPattern (string): regular expression to extract task name
    runPattern (string): regular expression to extract run number
    norp (bool): SUPPRESS rp_txt files creation (default false)
    noplot (bool): SUPPRESS plot files creation (default false)
    noeuc (bool): SUPPRESS using Euclidean distance instead of the 
        raw realigment parameters (default false)
    f_ind (list of strings): motion indicators to print in plot
    f_format (str): file format for plot (default '.png')
    f_height (float): plot height in inches (default 5.5)
    f_width (float): plot width in inches (default 7)









# * figHeight = plot height in inches
# * figWidth = plot width in inches
# * figDPI = plot resolution in dots per inch


Returns: 
    None: R script returns everything for now. Later 
    version the python script will return all info, 
    plots, etc. 

"""

import argparse,os,subprocess,sys

here = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
############
prog_descrip = 'Auto-motion fmriprep wrapper.'

def main(argv=sys.argv):
    arg_parser = argparse.ArgumentParser(description=prog_descrip,
                                         formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # Check for arguments. #
    if len(sys.argv[1:])==0:
        print('\nArguments required. Use -h option to print FULL usage.\n')

    arg_parser.add_argument('-b', metavar='BIDS Dir', action='store', required=True, type=os.path.abspath,
                            help=('FULL path to your top level bids folder.'),
                            dest='bids_dir'
                            )
    arg_parser.add_argument('-fig_ind', metavar='Motion Indicators', action='store', type=list,
                            required=False, default=['FramewiseDisplacement', 'GlobalSignal', 'stdDVARS'],
                            help=('motion indicators to print in plot.'),
                            dest='f_ind'
                            )
    arg_parser.add_argument('-fig_format', metavar='Fig File Format', action='store', type=str,
                            required=False, default='.png',
                            help=('file format for plot.'),
                            dest='f_format'
                            )
    arg_parser.add_argument('-fig_height', metavar='Fig Height', action='store', type=str,
                            required=False, default='5.5',
                            help=('plot height in inches.'),
                            dest='f_height'
                            )
    arg_parser.add_argument('-fig_width', metavar='Fig Width', action='store', type=str,
                            required=False, default='7',
                            help=('plot width in inches.'),
                            dest='f_width'
                            )
    arg_parser.add_argument('-fig_dpi', metavar='Fig DPI', action='store', type=str,
                            required=False, default='250',
                            help=('plot resolution in dots per inch.'),
                            dest='f_dpi'
                            )
    arg_parser.add_argument('-noeuc', action='store_true', required=False, default=False,
                            help=('Do NOT use euclidean distance. Uses RAW realignment \
                                parameters instead. This arg SUPPRESSES euclidean distance \
                                for realignment parameters.'),
                            dest='noeuc'
                            )
    arg_parser.add_argument('-norp', action='store_true', required=False, default=False,
                            help=('No rp_txt files. This arg SUPPRESSES file write.'),
                            dest='norp'
                            )
    arg_parser.add_argument('-noplot', action='store_true', required=False, default=False,
                            help=('No plots created. This arg SUPPRESSES plot creation.'),
                            dest='noplot'
                            )
    arg_parser.add_argument('-o', metavar='Ooutput Dir', action='store', required=False,
                            type=os.path.abspath, 
                            default=os.path.join(here,'auto_motion_output'), 
                            help=('Output dir if not default.'),
                            dest='out_dir'
                            )
    arg_parser.add_argument('-run', metavar='Run Reg', action='store', type=str, required=False,
                            help=('regular expression to extract run number.'),
                            dest='run_reg'
                            )
    arg_parser.add_argument('-s', metavar='Study Name', action='store', type=str, required=True,
                            help=('Study name.'),
                            dest='study'
                            )
    arg_parser.add_argument('-sub', metavar='Sub Reg', action='store', type=str, required=False,
                            help=('regular expression to extract subject ID.'),
                            dest='sub_reg'
                            )
    arg_parser.add_argument('-task', metavar='Task Reg', action='store', type=str, required=False,
                            help=('regular expression to extract task name.'),
                            dest='task_reg'
                            )
    arg_parser.add_argument('-wave', metavar='Wave Reg', action='store', type=str, required=False,
                            help=('regular expression to extract wave number.'),
                            dest='wave_reg'
                            )
    args = arg_parser.parse_args()

    confoundDir = os.path.join(args.bids_dir,'derivatives','fmriprep')
    summaryDir = os.path.join(args.out_dir,'summary')
    plotDir = os.path.join(args.out_dir,'plots')
    rpDir = os.path.join(args.out_dir,'rp_txt')

    ## testing ##
    args.sub_reg = 'sub-(.*[0-9]{3})'
    args.wave_reg = 'ses-wave([0-9]{1})'
    args.task_reg = 'task-(SVC|DSD)'
    args.run_reg = 'run-([0-9]{2})'


    if args.norp == True:
        norp = 'TRUE'
    else:
        norp = 'FALSE'

    if args.noplot == True:
        noplot = 'TRUE'
    else:
        noplot = 'FALSE'

    if args.noeuc == True:
        noeuc = 'TRUE'
    else:
        noeuc = 'FALSE'

    f_ind = ' '.join(args.f_ind)

    r_comm = ' '.join(['Rscript',
                       os.path.join(here,'auto_motion_fmriprep.R'),
                       confoundDir,
                       summaryDir,
                       rpDir,
                       plotDir,
                       args.study,
                       args.sub_reg,
                       args.wave_reg,
                       args.task_reg,
                       args.run_reg,
                       norp,
                       noplot,
                       noeuc,
                       '(' + f_ind + ')',
                       args.f_format,
                       args.f_height,
                       args.f_width,
                       args.f_dpi
                       ])
    # print(r_comm)
    subprocess.call(r_comm, shell=True)




if __name__ == '__main__':
    sys.exit(main())
