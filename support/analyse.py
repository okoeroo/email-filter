import os

from support.handleemail import read_eml
from support.filters import filter_emails_by_addresses, filter_emails_by_datetime_frame, filter_emails_by_keywords


# analyse .eml
# Each filter replies with a boolean.
# The final decision is a boolean
def analyse_file(config: list[str], filepath: str) -> bool:
    # only allow .eml
    if not filepath.endswith('.eml'):
        print("filepath not .eml", filepath)
        return False # mark as not a match

    # read and parse the email file into an Email object
    msg = read_eml(filepath)
        
    # Run filters
    if config['filter_datetime_frame_begin_datetime'] is not None and config['filter_datetime_frame_end_datetime'] is not None:
        ret_datetime_frame_matched = filter_emails_by_datetime_frame(config, msg)

    if config['email_addresses'] is not None:
        ret_emailaddress_matched = filter_emails_by_addresses(config, msg)

    if config['keywords'] is not None:
        ret_keyword_matched = filter_emails_by_keywords(config, msg)

    # Process as logical OR
    # if config['filter_logic'] == 'OR':
    #     if config['email_addresses'] is not None:
    #         ret_email_matched = filter_emails_by_addresses(config, msg)

    # TODO
    return True


# Walk dir and start analyses
def walk_and_analyse(config) -> None:
    for dirpath, dirnames, filenames in os.walk(config['tmp_pst_dir']):
        print(f'Found directory: {dirpath}')
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            
            print(f'Analysing file: {filepath}')
            match = analyse_file(config, filepath)
            if not match:
                print("Removing non-match:", filepath)
                os.unlink(filepath)