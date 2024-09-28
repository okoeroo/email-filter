import os


# Function to:
# - read the file, line by line
# - strip the line for prefixed and trailing whitespaces
# - lowercase the line
def read_file_strip_line_lower_case(file_path: str) -> list[str]:
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
        cleaned_lines = [line.strip().lower() for line in file.readlines()]
    return cleaned_lines


# Function to read email addresses from a file
def read_email_addresses(file_path: str) -> list[str]:
    return read_file_strip_line_lower_case(file_path)


# Function to read keywords from a file
def read_keywords(file_path: str) -> list[str]:
    return read_file_strip_line_lower_case(file_path)
