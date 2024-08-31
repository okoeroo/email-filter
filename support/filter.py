import datetime
from email.message import EmailMessage
from email.utils import parsedate_to_datetime
import pytz


# Function to read email addresses from a file
def read_email_addresses(file_path: str) -> list[str]:
    with open(file_path, 'r') as file:
        email_addresses = [line.strip().lower() for line in file.readlines()]
    return email_addresses


# Function to filter emails by a list of email addresses
def filter_emails_by_addresses(msg: EmailMessage, email_addresses: str,
                               begin_dt: datetime.datetime, end_dt: datetime.datetime) -> bool:
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