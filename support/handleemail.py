from email import policy
from email.message import EmailMessage
from email.parser import BytesParser
from support.filters_support_email import filter_emails_by_addresses, filter_emails_by_datetime_frame, filter_emails_by_keywords
from support.logging import write_log


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
    if config['filter']['datetime']['begin'] is not None and config['filter']['datetime']['end'] is not None:
        context['ret_datetime_frame_matched'] = filter_emails_by_datetime_frame(config, msg)

        # Unchangeable outcome, when the begin and end dates are set and the email is out of timeframe, this makes for an implicit mismatch.
        if not context['ret_datetime_frame_matched']:
            return context

    # Filter for emailaddress, when the list and config is set.
    if 'email_addresses' in config['filter'] and \
            'email_addresses' in config['filter']['emailaddresses'] and \
            config['filter']['emailaddresses']['email_addresses'] is not None:
        context['ret_emailaddress_matched'] = filter_emails_by_addresses(config, msg)

    # Filter for keywords, when the list and config is set.
    if 'keywords' in config['filter'] and \
            'list_of_keywords' in config['filter']['keywords'] and \
            config['filter']['keywords']['list_of_keywords'] is not None:
        context = filter_emails_by_keywords(config, context)

    # final verdict
    return context


### Run logical settings
def verdict_eml_filter_output(config: dict, context: dict) -> bool:
    if not context['ret_datetime_frame_matched']:
        if config['generic']['verbose']:
            write_log(config, f"No hit: out of timeframe. Related email: {context['filepath']}")
        return False

    if context['ret_emailaddress_matched'] or \
        context['ret_eml_keyword_matched'] or \
        context['ret_eml_attachment_keyword_matched']:

        items = []
        if context['ret_emailaddress_matched']:
            items.append("emailaddress(es)")

        if context['ret_eml_keyword_matched']:
            items.append("keyword(s)")

        if context['ret_eml_attachment_keyword_matched']:
            items.append("attachments")

        write_log(config, f"HIT: matched on [{", ".join(items)}]. Keyword hit on: {context['keyword_match']} in email: {context['filepath']}")
        return True

    # Otherwise, no match
    if config['generic']['verbose']:
        write_log(config, "No hit")
    return False