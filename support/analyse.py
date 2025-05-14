import os

from support.handleemail import read_eml
from email.message import EmailMessage
from support.filters import filter_emails_by_addresses, filter_emails_by_datetime_frame, filter_emails_by_keywords


def apply_filters(config: list[str], context: dict) -> dict:
    msg: EmailMessage = context['msg']

    ret_datetime_frame_matched = False
    ret_emailaddress_matched = False
    ret_keyword_matched = False

    # Filter for timeframe
    if config['filter_datetime_frame_begin_datetime'] is not None and config['filter_datetime_frame_end_datetime'] is not None:
        ret_datetime_frame_matched = filter_emails_by_datetime_frame(config, msg)

        # Unchangeable, when the begin and end dates are set and the email is out of timeframe, this makes for an implicit mismatch.
        if not ret_datetime_frame_matched:
            return (ret_datetime_frame_matched, ret_emailaddress_matched, ret_keyword_matched)

    # Filter for emailaddress, when the list and config is set.
    if config['email_addresses'] is not None:
        ret_emailaddress_matched = filter_emails_by_addresses(config, msg)

    # Filter for keywords, when the list and config is set.
    if config['keywords'] is not None:
        context = filter_emails_by_keywords(config, context)

    # Verdict
    context['ret_datetime_frame_matched'] = ret_datetime_frame_matched
    context['ret_emailaddress_matched'] = ret_emailaddress_matched
    return context


### Run logical settings
def verdict_filter_output(context: dict) -> bool:
    if not context['ret_datetime_frame_matched']:
        print("No hit: out of timeframe.")
        return False

    # Must match emailadress, and it did match. Then, if there is no keywords filter, this is the final answer.
    if context['ret_emailaddress_matched']  and not context['ret_keyword_matched']:
        print("HIT: matched on emailaddress")
        return True

    # Must match keyword, and it did match. Then, if there is no emailaddress filter, this is the final answer.
    if not context['ret_emailaddress_matched'] and context['ret_keyword_matched']:
        print(f"HIT: matched on keyword. Keyword hit on: \"{context['keyword_match']}\"")
        return True

    # If both keyword and emailaddresses are set, and both have "must match", then it's a logical and between them.
    if context['ret_emailaddress_matched'] and context['ret_keyword_matched']:
        print(f"HIT: matched on emailaddress and keyword. Keyword hit on: \"{context['keyword_match']}\"")
        return True

    # Otherwise, no match
    print("No hit")
    return False


# Cleanup a file: meaning, removing a file when, not in debug mode, a match
def cleanup_file(config: list[str], context: dict) -> None:
    # When not in debug mode, and no match, then remove the file
    if not config['debug'] and not context['match']:
        print("Removing non-match:", context['filepath'])
        os.unlink(context['filepath'])


# analyse .eml
# Each filter replies with a boolean.
# The final decision is a boolean
def analyse_file(config: list[str], filepath: str) -> None:
    context = {}

    # Add filepath to email in context
    context['filepath'] = filepath

    # only allow .eml
    if not filepath.endswith('.eml'):
        print(f"Filepath not .eml: {context['filepath']}")
        context['match'] = False

        # Cleanup file, keeping logic into account
        cleanup_file(config, context)
        return

    # Read and parse email
    context['msg'] = read_eml(context['filepath'])

    # Applying all the filter rules on the email
    context = apply_filters(config, context)

    # Return verdict value, hit = True, no hit = False
    context['match'] = verdict_filter_output(context)

    # Cleanup file, keeping logic into account
    cleanup_file(config, context)


# Walk dir and start analyses
def walk_and_analyse(config) -> None:
    if not os.path.exists(config['tmp_pst_dir']):
        raise FileNotFoundError(f"{config['tmp_pst_dir']} does not exist")

    for dirpath, dirnames, filenames in os.walk(config['tmp_pst_dir']):
        print(f'Found directory: {dirpath}')
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            
            print(f'Analysing file: {filepath}')
            match = analyse_file(config, filepath)
