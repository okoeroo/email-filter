from email.message import EmailMessage
from striprtf.striprtf import rtf_to_text
from email.utils import parsedate_to_datetime
from support.filter_support import remove_line_endings, find_exact_word, apply_filter_on_fulltext_by_keywords
from support.handlepdf import read_pdf_from_bytes_to_text
from support.handleics import read_ics_from_bytes_to_text
from support.handledocx import read_docx_from_bytes_to_text
import pytz
import pathlib


# Function to filter emails by a list of email addresses
def filter_emails_by_datetime_frame(config: dict, msg: EmailMessage) -> bool:
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
def filter_emails_by_addresses(config: dict, msg: EmailMessage) -> bool:
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


# Extract e-mail subject to processable text
def extract_subject_from_email(msg: EmailMessage) -> str:
    s = msg.get('subject')
    subject = remove_line_endings(s)
    return subject


# The purpose here is to exclusively extract the body, which could be Rich Text, as if it were an attachment
def extract_body_from_email(msg: EmailMessage) -> str:
    # 1. Probeer gewone text/plain of text/html body
    body = msg.get_body(preferencelist=('plain', 'html'))
    if body:
        return remove_line_endings(body.get_content())

    # 2. Doorloop alle onderdelen op zoek naar rtf-body.rtf
    for part in msg.walk():
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

    return None

# The purpose here is to extract the attachments and write them to disk and report in an list[str] where the str is the full path.
def extract_attachments_from_email(msg: EmailMessage) -> list[tuple[str, bytes]]:
    attachments = []

    for part in msg.walk():
        content_disposition = part.get("Content-Disposition", "")
        if content_disposition and "attachment" in content_disposition.lower():
            filename = part.get_filename()
            payload = part.get_payload(decode=True)  # binary data
            if filename and payload:
                attachments.append((filename, payload))

    return attachments


# Function to filter emails by a list of email addresses
def filter_emails_by_keywords(config: dict, context: dict) -> bool:
    msg: EmailMessage = context['msg']
    context['ret_eml_keyword_matched'] = False
    context['ret_eml_attachment_keyword_matched'] = False

    # input keywords to match
    keywords = config['keywords']

    subject = extract_subject_from_email(msg)
    body    = extract_body_from_email(msg)
    if not body:
        print(f"################## NO BODY: {context['filepath']}")
        ### Mogelijk moeten de attachments er nog uitgehaald worden.
        ### print(msg)
        ### print("################## NO BODY #####################")

    # The attachments list is an array of tuples with filepaths and payload in bytes
    attachments: list[tuple[str, bytes]] = extract_attachments_from_email(msg)
    attachments_matched = list[dict] 

    context['keyword_match'] = []

    if subject:
        for item in keywords:
            results_subject = find_exact_word(subject, item)
            context['ret_eml_keyword_matched'] = bool(results_subject)
            context['keyword_match'] += results_subject or []
            if bool(results_subject):
                return context

    if body:
        for item in keywords:
            results_body = find_exact_word(body, item)
            context['ret_eml_keyword_matched'] = bool(results_body)
            context['keyword_match'] += results_body or []
            if bool(results_body):
                return context

    if attachments:
        atleast_one_attachment_matched = False

        # Note: each attachment is evaluated. All will be checked. If one
        # matches, all will be written to disk.
        for att in attachments:
            # if "1606.eml" in context['filepath']:
                # print("inspect me")


            filename, data = att
            suffix = pathlib.Path(filename).suffix.lower()
            if suffix == ".pdf":
                pdfreader = read_pdf_from_bytes_to_text(data)

                if pdfreader:
                    # apply pdf filtering.
                    keyword_match = apply_filter_on_fulltext_by_keywords(config['keywords'], pdfreader)
                    context['keyword_match'] += keyword_match or []
                    if not atleast_one_attachment_matched:
                        atleast_one_attachment_matched = bool(keyword_match)

            if suffix == ".ics":
                gcal = read_ics_from_bytes_to_text(data)
                if gcal:
                    # Apply ICS filtering.
                    keyword_match = apply_filter_on_fulltext_by_keywords(config['keywords'], gcal)
                    context['keyword_match'] += keyword_match or []
                    if not atleast_one_attachment_matched:
                        atleast_one_attachment_matched = bool(keyword_match)

            if suffix == ".docx" or suffix == ".doc":
                doc = read_docx_from_bytes_to_text(data)
                if doc:
                    # Apply docx filtering.
                    keyword_match = apply_filter_on_fulltext_by_keywords(config['keywords'], doc)
                    context['keyword_match'] += keyword_match or []
                    if not atleast_one_attachment_matched:
                        atleast_one_attachment_matched = bool(keyword_match)


        # If one matched, write all to disk
        context['ret_eml_attachment_keyword_matched'] = atleast_one_attachment_matched
        if atleast_one_attachment_matched:
            for att in attachments:
                filename, data = att
                eml_filepath = context['filepath']

                path = pathlib.Path(eml_filepath)

                # Create a new directory path, based on the filename without suffix
                dir_path = path.with_name(path.stem)  # replaces 'document.pdf' with 'document'
                dir_path.mkdir(parents=True, exist_ok=True)

                # Add filename of the attachment, only allow unique names.
                orig_path = dir_path / filename
                full_path = unique_filename(orig_path)

                # Write bytestream
                with open(full_path, "wb") as f:
                    f.write(data)
                    print(f"Attachment written: {full_path}")

    # No match
    return context


def unique_filename(path: pathlib.Path) -> pathlib.Path:
    if not path.exists():
        return path

    counter = 1
    while True:
        new_name = f"{path.stem}__{counter}{path.suffix}"
        new_path = path.with_name(new_name)
        if not new_path.exists():
            return new_path
        counter += 1
