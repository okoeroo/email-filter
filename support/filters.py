import datetime
from email.message import EmailMessage
from email.utils import parsedate_to_datetime
import pytz


# Function to filter emails by a list of email addresses
def filter_emails_by_datetime_frame(config: list[str], msg: EmailMessage) -> bool:
    # Init
    begin_dt = config['begin_dt']
    end_dt = config['end_dt']
    local_timezone = config['local_timezone']

    # First filter - timeframe
    date_str = msg.get('date')
    if date_str is None:
        print(f"Warning: no datetime field found in email. Reporting as no match.")    
        return False

    # Convert
    date_value = parsedate_to_datetime(date_str)

    # If the date value is not time aware, force it to provided localtime
    if date_value.tzinfo is None:
        date_value = pytz.timezone(local_timezone).localize(date_value)

    # Check if the date_value is within the timeframe.
    if date_value >= begin_dt and date_value <= end_dt:
        print(f"HIT: email within datetime frame")
        return True

    # If the email address is outside of the time-frame.
    print(f"Info: Out of time frame: e-mail Date is {date_value.isoformat()}, which out of the {begin_dt.isoformat()} and {end_dt.isoformat()} window.")
    return False


# Function to filter emails by a list of email addresses
def filter_emails_by_addresses(config: list[str], msg: EmailMessage) -> bool:
    # Init
    email_addresses = config['email_addresses']
    email_addresses = [email.lower() for email in email_addresses]

    # From: ignore MAILER-DAEMON
    this_from = msg.get('From', '')
    if 'MAILER-DAEMON' in this_from:
        return False

    # Continue matching filter
    if any(email_address in this_from.lower() for email_address in email_addresses):
        print(f"HIT in From found")
        return True

    this_to = msg.get('To')
    if this_to is not None:
        if any(email_address in this_to.lower() for email_address in email_addresses):
            print(f"HIT in To found")
            return True

    this_cc = msg.get('Cc')
    if this_cc is not None:
        if any(email_address in this_cc.lower() for email_address in email_addresses):
            print(f"HIT in Cc found")
            return True

    this_bcc = msg.get('Bcc')
    if this_bcc is not None:
        if any(email_address in this_bcc.lower() for email_address in email_addresses):
            print(f"HIT in Bcc found")
            return True

    # If the email address is not found in any of the fields
    return False


# Function to filter emails by a list of email addresses
def filter_emails_by_keywords(config: list[str], msg: EmailMessage) -> bool:
    return True

    # Init
    email_addresses = config['email_addresses']
    email_addresses = [email.lower() for email in email_addresses]

    # From: ignore MAILER-DAEMON
    this_from = msg.get('From', '')
    if 'MAILER-DAEMON' in this_from:
        return False


    # First filter - timeframe
    date_str = msg.get('date')
    if date_str:
        date_value = parsedate_to_datetime(date_str)

        # If the date value is not time aware, force it to localtime
        if date_value.tzinfo is None:
            date_value = pytz.timezone('Europe/Amsterdam').localize(date_value)

        # Discard if out of timeframe
        if date_value < begin_dt or date_value > end_dt:
            print(f"Info: Out of time frame: e-mail Date is {date_value.isoformat()}, which out of the {begin_dt.isoformat()} and {end_dt.isoformat()} window.")
            return False


    # Second filter - addressing
    if any(email_address in this_from.lower() for email_address in email_addresses):
        print(f"HIT in From found")
        return True

    this_to = msg.get('To')
    if this_to is not None:
        if any(email_address in this_to.lower() for email_address in email_addresses):
            print(f"HIT in To found")
            return True

    this_cc = msg.get('Cc')
    if this_cc is not None:
        if any(email_address in this_cc.lower() for email_address in email_addresses):
            print(f"HIT in Cc found")
            return True

    this_bcc = msg.get('Bcc')
    if this_bcc is not None:
        if any(email_address in this_bcc.lower() for email_address in email_addresses):
            print(f"HIT in Bcc found")
            return True

    # If the email address is not found in any of the fields
    return False