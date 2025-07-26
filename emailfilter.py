#!/usr/bin/env python3

import os
from datetime import datetime
from tzlocal import get_localzone_name
import pytz

import shutil

from support.logging import open_log_file, write_log, close_log_file
from support.handlepst import run_readpst
from support.analyse import walk_and_analyse
from support.handlefiles import remove_empty_dirs
from support.setup_args import argparsing, setup


# Main program
def main(config: dict) -> None:
    # Test if the override switch if provided
    if config['unpacked_pst'] is None:
        # Run readpst on the PST file and into the temporary path
        try:
            run_readpst(config)
        except Exception as e:
            write_log(config, f"Error: {e}", level = "ERROR")
            write_log(config, f"Info: temporary directory is here: {config['tmp_pst_dir']}", stdout=True)
            return
    else:
        write_log(config, f"Override: Skipping the readpst processing. Pre-unpacked directory is \"{config['unpacked_pst']}\"", stdout=True)


    # if only PST unpacking, skip all.
    if config['only_pst_unpack']:
        write_log(config, f"Done. Location is: {config['tmp_pst_dir']}", stdout=True)
        return

    # Walk and analyse
    try:
        results = walk_and_analyse(config)
    except Exception as e:
        print(f"Error: {e}")
        return

    # Summary
    write_log(config, "=== Analyses of files ===", stdout=True)
    cnt = 0
    for context in results:
        if not context['match']:
            continue
        cnt += 1
        write_log(config, f"{cnt}: \"{os.path.basename(context['filepath'])}\"", stdout=True)

    # ************ Dry-run ON or OFF ************
    if config['dryrun']:
        write_log(config, f"DRYRUN: exiting without moving files. Location is: {config['tmp_pst_dir']}", stdout=True)
        return


    # Remove directories which are empty
    write_log(config, f"Removing empty directories from {config['tmp_pst_dir']}", stdout=True)
    remove_empty_dirs(config['tmp_pst_dir'])

    ### BLOCK
    return

    # Move
    write_log(config, "- Done -", stdout=True)
    write_log(config, f"Moving {config['tmp_pst_dir']} to {config['output_folder']}", stdout=True)
    shutil.move(config['tmp_pst_dir'], config['output_folder'])
    write_log(config, "===============================================", stdout=True)


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

    try:
        # Open logfile
        if config['logfile']:
            config = open_log_file(config)
            print(f"Logfile opened. Logging will continue in file \"{config['logfile']}\"")
            write_log(config, "========= Logging started =========")

        # Kick it off
        main(config)

    # Close logfile
    finally:
        close_log_file(config)