import os
import datetime

from support.handleemail import read_eml
from support.filter import filter_emails_by_addresses


# analyse .eml
def analyse_file(filepath: str, email_addresses: list[str],
                 begin_dt: datetime.datetime, end_dt: datetime.datetime) -> bool:
    # only allow .eml
    if not filepath.endswith('.eml'):
        print("filepath not .eml", filepath)
        return False # mark as not a match

    msg = read_eml(filepath)
    return filter_emails_by_addresses(msg, email_addresses, begin_dt, end_dt)


# Walk dir and start analyses
def walk_and_analyse(start_path: str, email_addresses: str, 
                     begin_dt: datetime.datetime, end_dt: datetime.datetime):
    for dirpath, dirnames, filenames in os.walk(start_path):
        print(f'Found directory: {dirpath}')
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            
            print(f'Analysing file: {filepath}')
            match = analyse_file(filepath, email_addresses, begin_dt, end_dt)
            if not match:
                print("Removing non-match:", filepath)
                os.unlink(filepath)