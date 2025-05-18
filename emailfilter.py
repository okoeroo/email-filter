#!/usr/bin/env python3

import os
from datetime import datetime
from tzlocal import get_localzone_name
import pytz

import shutil

from support.handlepst import run_readpst
from support.analyse import walk_and_analyse
from support.handlefiles import remove_empty_dirs, remove_files_not_matching_list_of_extentions
from support.setup_args import argparsing, setup


# Main program
def main(config: dict) -> None:
    # Test if the override switch if provided
    if config['unpacked_pst'] is None:
        # Run readpst on the PST file and into the temporary path
        try:
            run_readpst(config['tmp_pst_dir'], config['input_pst_path'])
        except Exception as e:
            print("Error:", e)
            print("Info: temporary directory is here:", config['tmp_pst_dir'])
            return
    else:
        print(f"Override: Skipping the readpst processing. Pre-unpacked directory is \"{config['unpacked_pst']}\"")


    # if only PST unpacking, skip all.
    if config['only_pst_unpack']:
        print(f"Done. Location is: {config['tmp_pst_dir']}")
        return

    # Walk and analyse
    results = walk_and_analyse(config)

    # Summary
    print("\n=== Analyses of files ===")
    cnt = 0
    for context in results:
        if not context['match']:
            continue
        cnt += 1
        print(f"{cnt}: \"{os.path.basename(context['filepath'])}\"")

    # ************ Dry-run ON or OFF ************
    if config['dryrun']:
        print(f"DRYRUN: exiting without moving files. Location is: {config['tmp_pst_dir']}")
        return

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
    # Gebruik bijvoorbeeld Europe/Amsterdam als tijdzone
    tz_name = get_localzone_name()
    tz = pytz.timezone(tz_name)
    now = datetime.now(tz)

    # Print in volledig ISO 8601 formaat
    print("Start tijd:", now.isoformat(), now.strftime("%d-%m-%Y %H:%M:%S %Z%z"))

    try:
        # Parse commandline arguments
        argp = argparsing(__file__)

        # Setup all the things
        config = setup(argp)

    except Exception as e:
        print(f"Error: {e}")

    # Kick it off
    main(config)
