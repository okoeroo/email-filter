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

        # Unchangeable, when the begin and end dates are set and the email is out of timeframe, this makes for an implicit mismatch.
        if not ret_datetime_frame_matched:
            return False

    # Filter for emailaddress, when the list and config is set.
    if config['email_addresses'] is not None:
        ret_emailaddress_matched = filter_emails_by_addresses(config, msg)

    # Filter for keywords, when the list and config is set.
    if config['keywords'] is not None:
        ret_keyword_matched = filter_emails_by_keywords(config, msg)


    ### Run logical settings

    # Must match emailadress, and it did match. Then, if there is no keywords filter, this is the final answer.
    if config['filter_match_emailaddresses_must_match'] == 'yes' and ret_emailaddress_matched and config['keywords'] is None:
        print("HIT: matched on emailaddress")
        return True

    # Must match keyword, and it did match. Then, if there is no emailaddress filter, this is the final answer.
    if config['filter_match_keywords_must_match'] == 'yes' and ret_keyword_matched and config['email_addresses'] is None:
        print("HIT: matched on keyword")
        return True

    # If both keyword and emailaddresses are set, and both have "must match", then it's a logical and between them.
    if config['filter_match_keywords_must_match'] == 'yes' \
            and ret_keyword_matched \
            and config['filter_match_emailaddresses_must_match'] == 'yes' \
            and ret_emailaddress_matched:
        print("HIT: matched on emailaddress and keyword")
        return True

    # Otherwise, no match
    print("No hit")
    return False


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