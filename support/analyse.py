import os

from support.handleemail import read_eml
from support.filter_emails_by_addresses import filter_emails_by_addresses


# analyse .eml
def analyse_file(config: list[str], filepath: str) -> bool:
    # only allow .eml
    if not filepath.endswith('.eml'):
        print("filepath not .eml", filepath)
        return False # mark as not a match

    msg = read_eml(filepath)
    return filter_emails_by_addresses(msg, config['email_addresses'], config['begin_dt'], config['end_dt'])


# Walk dir and start analyses
def walk_and_analyse(config) -> None:
    for dirpath, dirnames, filenames in os.walk(config['tmp_pst_dir']):
        print(f'Found directory: {dirpath}')
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            
            print(f'Analysing file: {filepath}')
            match = analyse_file(config, filepath)
            if not match:
                print("Removing non-match:", filepath)
                os.unlink(filepath)