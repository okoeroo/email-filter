import os
import re


# Perfect match
def find_exact_word(text: str, word: str) -> list[str]:
    pattern = rf'(?<![a-zA-Z]){re.escape(word)}(?![a-zA-Z])'
    return re.findall(pattern, text, flags=re.IGNORECASE)


# Remove line ending
def remove_line_endings(text: str) -> str:
    text = text.replace('\n\n', ' ').replace('\r\n', ' ')
    text = text.replace('\n', '').replace('\r', '')
    return text


# Function to:
# - read the file, line by line
# - strip the line for prefixed and trailing whitespaces
#### NO lower # - lowercase the line (or not)
def read_file_strip_line(file_path: str) -> list[str]:
    # Ignore
    if file_path is None:
        return None

    # Errors
    if not os.path.exists(file_path):
        raise f"the path {file_path} does not exist."

    if not os.path.isfile(file_path):
        raise f"the path {file_path} is not a file."

    # Read, strip, lower, append
    with open(file_path, 'r') as file:
        # cleaned_lines = [line.strip().lower() for line in file.readlines()]
        cleaned_lines = [line.strip() for line in file.readlines()]
    return cleaned_lines


# Function to read email addresses from a file
def read_email_addresses(file_path: str) -> list[str]:
    return read_file_strip_line(file_path)


# Function to read keywords from a file
def read_keywords(file_path: str) -> list[str]:
    return read_file_strip_line(file_path)
