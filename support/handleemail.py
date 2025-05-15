from email import policy
from email.message import EmailMessage
from email.parser import BytesParser
from support.filters_support_email import filter_emails_by_addresses, filter_emails_by_datetime_frame, filter_emails_by_keywords


# Function to read .eml file
def read_eml(filepath: str) -> EmailMessage:
    with open(filepath, 'rb') as file:
        msg = BytesParser(policy=policy.default).parse(file)
    return msg


def apply_eml_filters(config: dict, context: dict) -> dict:
    msg: EmailMessage = context['msg']

    context['ret_datetime_frame_matched'] = False
    context['ret_emailaddress_matched'] = False
    context['ret_eml_keyword_matched'] = False

    # Filter for timeframe
    if config['filter_datetime_frame_begin_datetime'] is not None and config['filter_datetime_frame_end_datetime'] is not None:
        context['ret_datetime_frame_matched'] = filter_emails_by_datetime_frame(config, msg)

        # Unchangeable outcome, when the begin and end dates are set and the email is out of timeframe, this makes for an implicit mismatch.
        if not context['ret_datetime_frame_matched']:
            return context

    # Filter for emailaddress, when the list and config is set.
    if config['email_addresses'] is not None:
        context['ret_emailaddress_matched'] = filter_emails_by_addresses(config, msg)

    # Filter for keywords, when the list and config is set.
    if config['keywords'] is not None:
        context = filter_emails_by_keywords(config, context)

    # final verdict
    return context


### Run logical settings
def verdict_eml_filter_output(context: dict) -> bool:
    if not context['ret_datetime_frame_matched']:
        print("No hit: out of timeframe.")
        return False

    # Must match emailadress, and it did match. Then, if there is no keywords filter, this is the final answer.
    if context['ret_emailaddress_matched']  and not context['ret_eml_keyword_matched']:
        print("HIT: matched on emailaddress")
        return True

    # Must match keyword, and it did match. Then, if there is no emailaddress filter, this is the final answer.
    if not context['ret_emailaddress_matched'] and context['ret_eml_keyword_matched']:
        print(f"HIT: matched on keyword. Keyword hit on: \"{context['keyword_match']}\"")
        return True

    # If both keyword and emailaddresses are set, and both have "must match", then it's a logical and between them.
    if context['ret_emailaddress_matched'] and context['ret_eml_keyword_matched']:
        print(f"HIT: matched on emailaddress and keyword. Keyword hit on: \"{context['keyword_match']}\"")
        return True

    # Otherwise, no match
    print("No hit")
    return False