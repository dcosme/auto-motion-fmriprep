#!/usr/bin/env python
#
""" Step one wrapper for auto motion fmriprep project. 
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
    norp (bool): SUPPRESS rp_txt files creation (default false)
    noplot (bool): SUPPRESS plot files creation (default false)
    noeuc (bool): SUPPRESS using Euclidean distance instead of the 
        raw realigment parameters (default false)
    f_ind (list of strings): motion indicators to print in plot
    f_format (str): file format for plot (default '.png')
    f_height (float): plot height in inches (default 5.5)
    f_width (float): plot width in inches (default 7)


Returns: 
    None: R script returns everything for now. Later 
    version the python script will return all info, 
    plots, etc. 

"""

import argparse,os,subprocess,sys

here = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))

############
prog_descrip = 'Auto-motion fmriprep wrapper.'

def tf(tfvar):
    if tfvar:
        return 'TRUE'
    else:
        return 'FALSE'


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
    arg_parser.add_argument('-o', metavar='Output Dir', action='store', required=False,
                            type=os.path.abspath, 
                            default=os.path.join(here,'auto_motion_output'), 
                            help=('Output dir if not default.'),
                            dest='out_dir'
                            )
    arg_parser.add_argument('-s', metavar='Study Name', action='store', type=str, required=True,
                            help=('Study name.'),
                            dest='study'
                            )
    arg_parser.add_argument('-fig_csf', action='store_true', 
                            required=False, default=False,
                            help=('Print CSF motion indicator in plot. If you select \
                                more than three total, you may need to adjust the \
                                figure dimensions'),
                            dest='f_csf'
                            )
    arg_parser.add_argument('-fig_wm', action='store_true', 
                            required=False, default=False,
                            help=('Print white matter motion indicator in plot. If you select \
                                more than three total, you may need to adjust the \
                                figure dimensions'),
                            dest='f_wm'
                            )
    arg_parser.add_argument('-fig_gs', action='store_true', 
                            required=False, default=True,
                            help=('Print global signal motion indicator in plot. If you select \
                                more than three total, you may need to adjust the \
                                figure dimensions'),
                            dest='f_gs'
                            )
    arg_parser.add_argument('-fig_dvars', action='store_true', 
                            required=False, default=False,
                            help=('Print non-standardized DVARS motion indicator in plot. If you select \
                                more than three total, you may need to adjust the \
                                figure dimensions'),
                            dest='f_dvars'
                            )
    arg_parser.add_argument('-fig_sdvars', action='store_true', 
                            required=False, default=True,
                            help=('Print standardized DVARS motion indicator in plot. If you select \
                                more than three total, you may need to adjust the \
                                figure dimensions'),
                            dest='f_sdvars'
                            )
    arg_parser.add_argument('-fig_vsdvars', action='store_true', 
                        required=False, default=False,
                        help=('Print voxel-wise standardized DVARS motion indicator in plot. If you select \
                            more than three total, you may need to adjust the \
                            figure dimensions'),
                        dest='f_vsdvars'
                        )
    arg_parser.add_argument('-fig_fd', action='store_true', 
                            required=False, default=True,
                            help=('Print framewise displacement motion indicator in plot. If you select \
                                more than three total, you may need to adjust the \
                                figure dimensions'),
                            dest='f_fd'
                            )
    arg_parser.add_argument('-fig_xtrans', action='store_true', 
                            required=False, default=False,
                            help=('Print x translation motion indicator in plot. If you select \
                                more than three total, you may need to adjust the \
                                figure dimensions'),
                            dest='f_xtrans'
                            )
    arg_parser.add_argument('-fig_ytrans', action='store_true', 
                            required=False, default=False,
                            help=('Print y translation motion indicator in plot. If you select \
                                more than three total, you may need to adjust the \
                                figure dimensions'),
                            dest='f_ytrans'
                            )
    arg_parser.add_argument('-fig_ztrans', action='store_true', 
                            required=False, default=False,
                            help=('Print z translation motion indicator in plot. If you select \
                                more than three total, you may need to adjust the \
                                figure dimensions'),
                            dest='f_ztrans'
                            )
    arg_parser.add_argument('-fig_xrot', action='store_true', 
                            required=False, default=False,
                            help=('Print x rotation motion indicator in plot. If you select \
                                more than three total, you may need to adjust the \
                                figure dimensions'),
                            dest='f_xrot'
                            )
    arg_parser.add_argument('-fig_yrot', action='store_true', 
                            required=False, default=False,
                            help=('Print y rotation motion indicator in plot. If you select \
                                more than three total, you may need to adjust the \
                                figure dimensions'),
                            dest='f_yrot'
                            )
    arg_parser.add_argument('-fig_zrot', action='store_true', 
                            required=False, default=False,
                            help=('Print z rotation motion indicator in plot. If you select \
                                more than three total, you may need to adjust the \
                                figure dimensions'),
                            dest='f_zrot'
                            )
    args = arg_parser.parse_args()

    r_comm = ' '.join(['Rscript',
                       os.path.join(here,'auto_motion_fmriprep.R'),
                       os.path.join(args.bids_dir,'derivatives','fmriprep'),
                       os.path.join(args.out_dir,'summary'),
                       os.path.join(args.out_dir,'rp_txt'),
                       os.path.join(args.out_dir,'plots'),
                       args.study,
                       tf(args.norp),
                       tf(args.noplot),
                       tf(args.noeuc),
                       args.f_format,
                       args.f_height,
                       args.f_width,
                       args.f_dpi,
                       tf(args.f_csf),
                       tf(args.f_wm),
                       tf(args.f_gs),
                       tf(args.f_dvars),
                       tf(args.f_sdvars),
                       tf(args.f_vsdvars),
                       tf(args.f_fd),
                       tf(args.f_xtrans),
                       tf(args.f_ytrans),
                       tf(args.f_ztrans),
                       tf(args.f_xrot),
                       tf(args.f_yrot),
                       tf(args.f_zrot)])

    #print(r_comm)
    subprocess.call(r_comm, shell=True)


if __name__ == '__main__':
    sys.exit(main())
