import os

from support.filter import read_email_addresses
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
    parser.add_argument("--input-pst-path",
                        dest="input_pst_path",
                        help="Input PST file.",
                        required=True,
                        type=str)
    parser.add_argument("--file-with-emailaddresses",
                        dest="file_with_emailaddresses",
                        help="File with emailaddresses",
                        required=False,
                        type=str)
    parser.add_argument("--output-folder",
                        dest="output_folder",
                        help="This is the output directory in which all results will be moved into",
                        required=True,
                        type=str)
    parser.add_argument("--begin-datetime",
                        dest="begin_datetime",
                        help="Begin datetime, optional with timezone",
                        required=False,
                        type=str)
    parser.add_argument("--end-datetime",
                        dest="end_datetime",
                        help="End datetime, optional with timezone",
                        required=False,
                        type=str)
    parser.add_argument("--local-timezone",
                        dest="local_timezone",
                        help="Set the local timezone, default is \'Europe/Amsterdam\'",
                        default='Europe/Amsterdam',
                        required=False,
                        type=str)

    return parser.parse_args()


# Setup
def setup(argp):
    config = {}

    config['exec'] = os.path.basename(__file__)
    config['verbose'] = argp.verbose
    config['input_pst_path'] = argp.input_pst_path
    config['file_with_emailaddresses'] = argp.file_with_emailaddresses
    config['output_folder'] = argp.output_folder
    config['begin_datetime'] = argp.begin_datetime
    config['end_datetime'] = argp.end_datetime
    config['local_timezone'] = argp.local_timezone

    # Set default timezone to use as the local timezone
    set_localtime(argp.local_timezone)

    # Setup scratch directory
    tmp_pst_dir = create_random_named_directory()
    print("Temporary of unpack directory for the PST source file:", tmp_pst_dir)
    config['tmp_pst_dir'] = tmp_pst_dir

    # Read input for email addresses
    print("Input file for the list of emailaddressess to filter:", argp.file_with_emailaddresses)
    email_addresses = read_email_addresses(argp.file_with_emailaddresses)
    config['email_addresses'] = email_addresses
    
    # Parse ISO Format into datetime
    begin_dt = parse_datetime_isoformat(argp.begin_datetime)
    end_dt = parse_datetime_isoformat(argp.end_datetime)

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