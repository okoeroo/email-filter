from email import policy
from email.message import EmailMessage
from email.parser import BytesParser


# Function to read .eml file
def read_eml(filepath: str) -> EmailMessage:
    with open(filepath, 'rb') as file:
        msg = BytesParser(policy=policy.default).parse(file)
    return msg

