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
    parser.add_argument("--local-timezone",
                        dest="local_timezone",
                        help="Set the local timezone, default is \'Europe/Amsterdam\'",
                        default='Europe/Amsterdam',
                        required=False,
                        type=str)

    parser.add_argument("--input-pst-path",
                        dest="input_pst_path",
                        help="Input PST file.",
                        required=True,
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

    parser.add_argument("--output-folder",
                        dest="output_folder",
                        help="This is the output directory in which all results will be moved into",
                        required=True,
                        type=str)

    return parser.parse_args()


# Setup
def setup(argp):
    config = {}

    config['exec'] = os.path.basename(__file__)
    config['verbose'] = argp.verbose
    config['local_timezone'] = argp.local_timezone
    config['input_pst_path'] = argp.input_pst_path
    config['filter_match_emailaddresses_file_path'] = argp.filter_match_emailaddresses_file_path
    config['filter_match_emailaddresses_must_match'] = argp.filter_match_emailaddresses_must_match
    config['filter_match_keywords_file_path'] = argp.filter_match_keywords_file_path
    config['filter_match_keywords_must_match'] = argp.filter_match_keywords_must_match
    config['filter_datetime_frame_begin_datetime'] = argp.filter_datetime_frame_begin_datetime
    config['filter_datetime_frame_end_datetime'] = argp.filter_datetime_frame_end_datetime
    config['output_folder'] = argp.output_folder

    # Set default timezone to use as the local timezone
    set_localtime(argp.local_timezone)

    # Setup scratch directory
    tmp_pst_dir = create_random_named_directory()
    print("Temporary of unpack directory for the PST source file:", tmp_pst_dir)
    config['tmp_pst_dir'] = tmp_pst_dir

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

    return config