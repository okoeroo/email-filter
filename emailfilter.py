import shutil

from support.handlepst import run_readpst
from support.analyse import walk_and_analyse
from support.handlefiles import remove_empty_dirs, remove_files_not_matching_list_of_extentions
from support.setup_args import argparsing, setup


# Main program
def main(config: dict) -> None:
    # Run readpst on the PST file and into the temporary path
    rc = run_readpst(config['tmp_pst_dir'], config['input_pst_path'])
    if rc != 0:
        print("Reading PST failed:", rc)
        raise Exception("readpst failed with error core {rc}")
    
    # Remove not matching extentions
    remove_files_not_matching_list_of_extentions(config['tmp_pst_dir'], ['.eml'])

    # Walk and analyse
    walk_and_analyse(config['tmp_pst_dir'], config['email_addresses'], config['begin_dt'], config['end_dt'])

    # Remove directories which are empty
    print(f"Removing empty directories from {config['tmp_pst_dir']}")
    remove_empty_dirs(config['tmp_pst_dir'])

    # Move
    print("- Done -")
    print(f"Moving {config['tmp_pst_dir']} to {config['output_folder']}")
    shutil.move(config['tmp_pst_dir'], config['output_folder'])
    print("===============================================")


# Start
if __name__ == "__main__":
    # Parse commandline arguments
    argp = argparsing(__file__)

    # Setup all the things
    config = setup(argp)

    # Kick it off
    main(config)