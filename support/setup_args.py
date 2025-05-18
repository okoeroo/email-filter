import os

from support.filter_support import read_email_addresses, read_keywords
from support.handlefiles import create_random_named_directory
from support.handledatetime import set_localtime, localize_datetime, parse_datetime_isoformat


def argparsing(scriptpath):
    # Parser
    import os
    import argparse

    parser = argparse.ArgumentParser(os.path.basename(scriptpath))
    parser.add_argument("-v", "--verbose",
                        dest="verbose",
                        help="Verbose mode. Default is off",
                        action="store_true",
                        default=False)

    parser.add_argument("--dryrun",
                        dest="dryrun",
                        help="Dryrun mode. It will not write, move or remove files. Default is off",
                        action="store_true",
                        default=False)

    parser.add_argument("--debug",
                        dest="debug",
                        help="Debug mode. Default is off",
                        action="store_true",
                        default=False)

    parser.add_argument("--only-pst-unpack",
                        dest="only_pst_unpack",
                        help="Only unpack the PST file. All other options are discarded",
                        action="store_true",
                        default=False)

    parser.add_argument("--local-timezone",
                        dest="local_timezone",
                        help="Set the local timezone, default is \'Europe/Amsterdam\'",
                        default='Europe/Amsterdam',
                        required=False,
                        type=str)

    parser.add_argument("--input-pst-path",
                        dest="input_pst_path",
                        help="Input PST file.",
                        required=False,
                        type=str)

    parser.add_argument("--filter-match-emailaddresses-file-path",
                        dest="filter_match_emailaddresses_file_path",
                        help="Filepath to a file which lists emailaddresses to match. When any emailaddress matches To, CC, BCC or From the mail is selected. When not set, no filter is applied on sender nor recipients.",
                        required=False,
                        default=None,
                        type=str)
    parser.add_argument("--filter-match-emailaddresses-must-match",
                        dest="filter_match_emailaddresses_must_match",
                        help="When an emailaddress is on the list and 'yes' is set, the email is matched. When 'no' is set, the email will not match.",
                        choices=['yes', 'no'],
                        required=False,
                        default='no',
                        type=str)

    parser.add_argument("--filter-match-keywords-file-path",
                        dest="filter_match_keywords_file_path",
                        help="Filepath to a file which lists keywords to match. When any keyword matches, the email is selected. When not set, no mails are filtered",
                        required=False,
                        default=None,
                        type=str)
    parser.add_argument("--filter-match-keywords-must-match",
                        dest="filter_match_keywords_must_match",
                        help="When an keyword is on the list and 'yes' is set, the keyword is matched. When 'no' is set, the keyword will not match.",
                        choices=['yes', 'no'],
                        required=False,
                        default='no',
                        type=str)

    parser.add_argument("--filter-timeframe-begin-datetime",
                        dest="filter_datetime_frame_begin_datetime",
                        help="Begin datetime in ISO format, optional with timezone. Example: 2001-01-01T00:00:00+01:00",
                        required=False,
                        default=None,
                        type=str)
    parser.add_argument("--filter-timeframe-end-datetime",
                        dest="filter_datetime_frame_end_datetime",
                        help="End datetime in ISO format, optional with timezone. Example: 2030-01-24T23:59:59+01:00",
                        required=False,
                        default=None,
                        type=str)

    parser.add_argument("--unpacked-pst",
                        dest="unpacked_pst",
                        help="This is the input directory from which an unpacked PST is expected.",
                        required=False,
                        default=None,
                        type=str)

    parser.add_argument("--output-folder",
                        dest="output_folder",
                        help="This is the output directory in which all results will be moved into",
                        required=False,
                        type=str)

    parser.add_argument("--threads",
                        dest="threads",
                        help="Set the amount of threads for the file handling",
                        required=False,
                        default=8,
                        type=int)
                    

    return parser.parse_args()


# Setup
def setup(argp):
    config = {}

    config['exec'] = os.path.basename(__file__)
    config['verbose'] = argp.verbose
    config['dryrun'] = argp.dryrun
    config['debug'] = argp.debug
    config['local_timezone'] = argp.local_timezone
    config['input_pst_path'] = argp.input_pst_path
    config['unpacked_pst'] = argp.unpacked_pst
    config['only_pst_unpack'] = argp.only_pst_unpack
    config['threads'] = argp.threads
    config['filter_match_emailaddresses_file_path'] = argp.filter_match_emailaddresses_file_path
    config['filter_match_emailaddresses_must_match'] = argp.filter_match_emailaddresses_must_match
    config['filter_match_keywords_file_path'] = argp.filter_match_keywords_file_path
    config['filter_match_keywords_must_match'] = argp.filter_match_keywords_must_match
    config['filter_datetime_frame_begin_datetime'] = argp.filter_datetime_frame_begin_datetime
    config['filter_datetime_frame_end_datetime'] = argp.filter_datetime_frame_end_datetime
    config['output_folder'] = argp.output_folder

    # Sanity check
    if bool(config['filter_datetime_frame_begin_datetime'] is not None) ^ bool(config['filter_datetime_frame_end_datetime'] is not None): 
        raise TypeError("Error: a begin or end date is set, but not both.")

    # Set default timezone to use as the local timezone
    set_localtime(argp.local_timezone)

    # When unpacked_pst is selected and only PST unpack is selected, fail initialisation
    if config['unpacked_pst'] is not None and config['only_pst_unpack']:
        raise ValueError("Incompatible arguments: --unpacked-pst is incompatible with --only-pst-unpack.")

    # Is scratch directory for PST unpacking needed?
    if config['unpacked_pst'] is None:
        # Setup scratch directory
        tmp_pst_dir = create_random_named_directory()
        print("Temporary of unpack directory for the PST source file:", tmp_pst_dir)
        config['tmp_pst_dir'] = tmp_pst_dir
    else:
        # PST file is unpacked already
        print("Provided PST unpack directory for the PST source file:", config['unpacked_pst'])
        config['tmp_pst_dir'] = config['unpacked_pst']

    # Read input for email addresses
    print("Input file for the list of emailaddressess to filter:", argp.filter_match_emailaddresses_file_path)
    email_addresses = read_email_addresses(argp.filter_match_emailaddresses_file_path)
    config['email_addresses'] = email_addresses

    # Read input for keywords
    print("Input file for the list of keywords to filter:", argp.filter_match_keywords_file_path)
    keywords = read_keywords(argp.filter_match_keywords_file_path)
    config['keywords'] = keywords
    
    # Parse ISO Format into datetime
    begin_dt = parse_datetime_isoformat(argp.filter_datetime_frame_begin_datetime)
    end_dt = parse_datetime_isoformat(argp.filter_datetime_frame_end_datetime)

    # Add TZ info if absent
    if begin_dt.tzinfo is None:
        begin_dt = localize_datetime(begin_dt)

    if end_dt.tzinfo is None:
        end_dt = localize_datetime(end_dt)

    config['begin_dt'] = begin_dt
    config['end_dt'] = end_dt

    print("Filter From:", begin_dt.isoformat())
    print("      Until:", end_dt.isoformat())

    # Dry-run mode?
    print(f"***** DRY RUN MODE: {'On' if config['dryrun'] else 'Off'} *****")

    # Only PST unpacking
    if config['only_pst_unpack']:
        print("*** Only unpack PST file ***")

    return config