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

    parser.add_argument("--config-file",
                        dest="configfile",
                        help="Configuration file to use. Set a file path.",
                        required=True,
                        default=None,
                        type=str)

    parser.add_argument("--logfile",
                        dest="logfile",
                        help="Path for the logfile output",
                        required=False,
                        default=None,
                        type=str)

    parser.add_argument("--stop-after-unpack",
                        dest="stop_after_unpack",
                        help="Only unpack the PST file. All other options are discarded",
                        action="store_true",
                        default=False)

    parser.add_argument("--local-timezone",
                        dest="local_timezone",
                        help="Set the local timezone, default is \'Europe/Amsterdam\'",
                        default=None,
                        required=False,
                        type=str)

    parser.add_argument("--input-pst-path",
                        dest="input_pst_path",
                        help="Input PST file.",
                        default=None,
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
                        default=None,
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
                        default=None,
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
                        type=str)

    parser.add_argument("--output-folder",
                        dest="output_folder",
                        help="This is the output directory in which all results will be moved into",
                        required=False,
                        type=str)

    parser.add_argument("--threads",
                        dest="threads",
                        help="Set the amount of threads for the readpst handling",
                        required=False,
                        default=None,
                        type=int)
                    
    parser.add_argument("--async-parallelism",
                        dest="async_parallelism",
                        help="Set the amount of asyncio parallel workers",
                        required=False,
                        default=None,
                        type=int)

    return parser.parse_args()


# Read TOML file
def read_toml_config_file(filepath: str) -> dict | None:
    import tomllib

    try:
        print(f"Using TOML file: {filepath}")
        with open(filepath, "rb") as f:
            config = tomllib.load(f)
    except FileNotFoundError:
        print("TOML file not found.")
        return None
    except tomllib.TOMLDecodeError as e:
        print(f"Invalid TOML syntax: {e}")
        return None
    except OSError as e:
        print(f"General I/O error: {e}")
        return None

    return config


# Setup
def setup():
    # Parse commandline arguments
    argp = argparsing(__file__)

    # Parse TOML config.
    config = read_toml_config_file(argp.configfile)
    if config is None:
        return

    if 'generic' not in config:                     config['generic'] = {}
    if 'run' not in config:                         config['run'] = {}
    if 'input' not in config:                       config['input'] = {}
    if 'intermediate' not in config:                config['intermediate'] = {}
    if 'output' not in config:                      config['output'] = {}
    if 'filter' not in config:                      config['filter'] = {}
    if 'datetime' not in config['filter']:          config['filter']['datetime'] = {}
    if 'emailaddresses' not in config['filter']:    config['filter']['emailaddresses'] = {}
    if 'keywords' not in config['filter']:          config['filter']['keywords'] = {}

    # Combine argparsing with TOML
    config['exec'] = os.path.basename(__file__)
    if argp.verbose:                        config['generic']['verbose'] = argp.verbose
    if argp.dryrun:                         config['generic']['dryrun'] = argp.dryrun
    if argp.debug:                          config['generic']['debug'] = argp.debug
    if argp.logfile is not None:            config['run']['logfile'] = argp.logfile
    if argp.local_timezone is not None:     config['run']['local_timezone'] = argp.local_timezone
    if argp.threads is not None:            config['run']['threads'] = argp.threads
    if argp.async_parallelism is not None:  config['run']['async_parallelism'] = argp.async_parallelism
    if argp.input_pst_path is not None:     config['input']['input_pst_path'] = argp.input_pst_path
    if argp.unpacked_pst:                   config['intermediate']['unpacked_pst'] = argp.unpacked_pst
    if argp.stop_after_unpack:              config['intermediate']['stop_after_unpack'] = argp.stop_after_unpack
    if argp.output_folder is not None:      config['output']['output_folder'] = argp.output_folder
    

    if argp.filter_datetime_frame_begin_datetime is not None:   config['filter']['datetime']['begin'] = argp.filter_datetime_frame_begin_datetime
    if argp.filter_datetime_frame_end_datetime is not None:     config['filter']['datetime']['end'] = argp.filter_datetime_frame_end_datetime
    if argp.filter_match_emailaddresses_file_path is not None:  config['filter']['emailaddresses']['file_path'] = argp.filter_match_emailaddresses_file_path
    if argp.filter_match_emailaddresses_must_match is not None: config['filter']['emailaddresses']['must_match'] = argp.filter_match_emailaddresses_must_match
    if argp.filter_match_keywords_file_path is not None:        config['filter']['keywords']['file_path'] = argp.filter_match_keywords_file_path
    if argp.filter_match_keywords_must_match is not None:       config['filter']['keywords']['must_match'] = argp.filter_match_keywords_must_match


    if config['run']['threads'] is None:
        config['run']['threads'] = 8    

    if 'async_parallelism' not in config or config['run']['async_parallelism'] is None:
        config['run']['async_parallelism'] = 10

    # Set default timezone to use as the local timezone
    set_localtime(config['run']['local_timezone'] )

    # Is scratch directory for PST unpacking needed?
    if config['intermediate']['unpacked_pst'] is None:
        # Setup scratch directory
        tmp_pst_dir = create_random_named_directory()
        print("Temporary of unpack directory for the PST source file:", tmp_pst_dir)
        config['intermediate']['unpacked_pst'] = tmp_pst_dir

    # PST file is unpacked already
    print("Provided PST unpack directory for the PST source file:", config['intermediate']['unpacked_pst'])

    # Read input for email addresses
    if 'file_path' in config['filter']['emailaddresses']:
        print("Input file for the list of emailaddressess to filter:", config['filter']['emailaddresses']['file_path'])
        email_addresses = read_email_addresses(config['filter']['emailaddresses']['file_path'])
        config['filter']['emailaddresses']['email_addresses'] = email_addresses

    # Read input for keywords
    if 'file_path' in config['filter']['keywords']:
        print("Input file for the list of keywords to filter:", config['filter']['keywords']['file_path'])
        keywords = read_keywords(config['filter']['keywords']['file_path'])
        config['filter']['keywords']['list_of_keywords'] = keywords
    
    # Parse ISO Format into datetime
    if bool(config['filter']['datetime']['begin'] is not None) ^ bool(config['filter']['datetime']['end'] is not None): 
        raise TypeError("Error: a begin or end date is set, but not both or none of the two.")

    begin_dt = parse_datetime_isoformat(config['filter']['datetime']['begin'])
    end_dt = parse_datetime_isoformat(config['filter']['datetime']['end'])

    # Add TZ info if absent
    if begin_dt.tzinfo is None:
        begin_dt = localize_datetime(begin_dt)

    if end_dt.tzinfo is None:
        end_dt = localize_datetime(end_dt)

    config['filter']['datetime']['begin_dt'] = begin_dt
    config['filter']['datetime']['end_dt'] = end_dt

    print("Filter From:", begin_dt.isoformat())
    print("      Until:", end_dt.isoformat())

    # Dry-run mode?
    print(f"***** DRY RUN MODE: {'On' if config['generic']['dryrun'] else 'Off'} *****")

    # Only PST unpacking
    if config['intermediate']['stop_after_unpack']:
        print("*** Only unpack PST file ***")

    return config