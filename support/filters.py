from email import message_from_string
from email import policy
from email import message_from_bytes, policy
from email.message import EmailMessage
from striprtf.striprtf import rtf_to_text
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
        if config['verbose']:
            print(f"Warning: no datetime field found in email. Reporting as no match.")    
        return True # Don't discard based on format failures

    # Convert
    date_value = parsedate_to_datetime(date_str)

    # If the date value is not time aware, force it to provided localtime
    if date_value.tzinfo is None:
        date_value = pytz.timezone(local_timezone).localize(date_value)

    # Check if the date_value is within the timeframe.
    if date_value >= begin_dt and date_value <= end_dt:
        if config['verbose']:
            print(f"HIT: email within datetime frame")
        return True

    # If the email address is outside of the time-frame.
    if config['verbose']:
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


# Remove line ending
def remove_line_endings(text: str) -> str:
    text = text.replace('\n\n', ' ').replace('\r\n', ' ')
    text = text.replace('\n', '').replace('\r', '')
    return text


# Extract e-mail subject to processable text
def extract_subject_from_email(msg: EmailMessage) -> str:
    s = msg.get('subject')
    subject = remove_line_endings(s).lower()
    return subject


# Extract e-mail body to processable text
def extract_body_from_email(msg: EmailMessage, preferencelist: str) -> str:
    charset = msg.get_content_charset() or 'utf-8'
    body_variant = msg.get_body(preferencelist=preferencelist)
    if body_variant:
        s = str(body_variant)
        body_variant = remove_line_endings(s).lower()
    return body_variant


# The purpose here is to exclusively extract the body, which could be Rich Text, as if it were an attachment
def extract_body_from_email(msg: EmailMessage) -> str:
    # 1. Probeer gewone text/plain of text/html body
    body = msg.get_body(preferencelist=('plain', 'html'))
    if body:
        return remove_line_endings(body.get_content())

    # 2. Doorloop alle onderdelen op zoek naar rtf-body.rtf
    for part in msg.walk():
        content_disposition = part.get("Content-Disposition", "")
        filename = part.get_filename()
        if filename and filename.lower() == "rtf-body.rtf":
            # Decode payload veilig
            payload = part.get_payload(decode=True)
            try:
                rtf_str = payload.decode('utf-8')
            except UnicodeDecodeError:
                rtf_str = payload.decode('latin1', errors='replace')

            # Converteer RTF naar platte tekst
            return remove_line_endings(rtf_to_text(rtf_str))
        else:
            print("DEBUG: filename", filename)

    return None

# Function to filter emails by a list of email addresses
def filter_emails_by_keywords(config: list[str], context: dict) -> bool:
    msg: EmailMessage = context['msg']
    context['ret_keyword_matched'] = False

    # input keywords to match
    keywords = config['keywords']

    # Lowercase subject and body in all formats
    subject = extract_subject_from_email(msg)
    body    = extract_body_from_email(msg)
    if not body:
        print("################## NO BODY #####################")
        ### Mogelijk moeten de attachments er nog uitgehaald worden.
        ### print(msg)
        ### print("################## NO BODY #####################")

    # Match: does keyword exist in string
    for item in keywords:
        if subject and item in subject:
            context['ret_keyword_matched'] = True
            context['keyword_match'] = item
            return context

        if body and item in body:
            context['ret_keyword_matched'] = True
            context['keyword_match'] = item
            return context

    # No match
    return context

