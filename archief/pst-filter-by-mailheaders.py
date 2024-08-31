import pypff
import os
from email import policy
from email.message import EmailMessage
from email.generator import BytesGenerator
from email.header import make_header, decode_header
from email.utils import formataddr
from io import BytesIO



# Function to read email addresses from a file
def read_email_addresses(file_path):
    with open(file_path, 'r') as file:
        email_addresses = [line.strip().lower() for line in file.readlines()]
    return email_addresses

# Function to read emails from a PST file
def read_pst_file(file_path):
    pst = pypff.open(file_path)
    
    root_folder = pst.get_root_folder()
    messages = []

    def recursively_read_folder(folder):
        for item in folder.sub_items:
            if isinstance(item, pypff.message):
                messages.append(item)
            elif isinstance(item, pypff.folder):
                recursively_read_folder(item)
                
    recursively_read_folder(root_folder)
    return messages

# Function to filter emails by a list of email addresses
def filter_emails_by_addresses(messages, email_addresses):
    filtered_messages = []
    email_addresses = [email.lower() for email in email_addresses]

    for message in messages:
        header = message.transport_headers.lower() if message.transport_headers else ""
        if any(email in header for email in email_addresses):
            filtered_messages.append(message)
    
    return filtered_messages

# Function to parse transport headers
def parse_headers(headers):
    parsed_headers = {}
    for line in headers.splitlines():
        if line.startswith(" ") or line.startswith("\t"):
            # Handle folded headers
            last_key = list(parsed_headers.keys())[-1]
            parsed_headers[last_key] += " " + line.strip()
        else:
            if ": " in line:
                key, value = line.split(": ", 1)
                parsed_headers[key] = str(make_header(decode_header(value)))
    return parsed_headers

# Function to save filtered emails to EML files
def save_to_eml_files(filtered_messages, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for i, message in enumerate(filtered_messages):
        eml_path = os.path.join(output_folder, f"filtered_email_{i+1}.eml")
        
        # Create the email message
        email_message = EmailMessage()
        # email_message['Subject'] = message.subject
        # email_message['From'] = message.sender_name
        # email_message['To'] = message.display_to
        # email_message['Cc'] = message.display_cc
        # email_message['Bcc'] = message.display_bcc

#        print(message.transport_headers)
        
        headers = parse_headers(message.transport_headers)
        for name, value in headers.items():
            email_message.add_header(name, value)

        # Set the email body (HTML or plain text)
        if message.html_body:
            email_message.set_content(message.html_body, maintype=email_message.get_content_type(), subtype='html')
        elif message.plain_text_body:
            email_message.set_content(message.plain_text_body, maintype=email_message.get_content_type(), subtype='plain')

        # Attachments
        for attachment in message.attachments:
            size = attachment.get_size()
            data = attachment.read_buffer(size)

            email_message.add_attachment(data)

            # email_message.add_attachment(
            #     attachment.read_buffer(size),
            #     maintype=attachment.mime_type.split('/')[0],
            #     subtype=attachment.mime_type.split('/')[1],
            #     filename=attachment.name
            # )


        # Save to EML
        with open(eml_path, 'wb') as f:
            generator = BytesGenerator(f, policy=policy.default)
            generator.flatten(email_message)

            print(email_message)


# Main program
def main(input_pst_path, email_addresses_file, output_folder):
    email_addresses = read_email_addresses(email_addresses_file)
    messages = read_pst_file(input_pst_path)
    filtered_messages = filter_emails_by_addresses(messages, email_addresses)
    save_to_eml_files(filtered_messages, output_folder)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 4:
        print(sys.argv)
        print("Usage: filter_eml_with_pypff.py <input_pst_path> <email_addresses_file> <output_folder>")
        sys.exit(1)

    input_pst_path = sys.argv[1]
    email_addresses_file = sys.argv[2]
    output_folder = sys.argv[3]

    main(input_pst_path, email_addresses_file, output_folder)