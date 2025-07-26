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
from support.setup_args import setup


# Phase 1: unpacking of PST
def phase1_unpack_pst_into_directory(config: dict) -> None:
    # Run readpst on the PST file and into the temporary path
    try:
        run_readpst(config)
    except Exception as e:
        write_log(config, f"Error: {e}", level = "ERROR")
        write_log(config, f"Info: temporary directory is here: {config['intermediate']['unpacked_pst']}", stdout=True)
        return


# Phase 2: process and filter the unpacked directory
def phase2_process_and_filter_unpacked_dir(config: dict) -> list | None:
    # Walk and analyse
    try:
        results = walk_and_analyse(config)
        return results

    except Exception as e:
        print(f"Error: {e}")
        return None


# Phase 3: summary and clean up
def phase3_summary_and_clean_up(config: dict, results: list | None) -> None:
    # Summary
    write_log(config, "=== Analyses of files ===", stdout=True)
    cnt = 0
    for context in results or []:
        if not context['match']:
            continue
        cnt += 1
        write_log(config, f"{cnt}: \"{os.path.basename(context['filepath'])}\"", stdout=True)

    # ************ Dry-run ON or OFF ************
    if config['generic']['dryrun']:
        write_log(config, f"DRYRUN: exiting without moving files. Location is: {config['intermediate']['unpacked_pst']}", stdout=True)
        return


    # Remove directories which are empty
    write_log(config, f"Removing empty directories from {config['intermediate']['unpacked_pst']}", stdout=True)
    remove_empty_dirs(config['intermediate']['unpacked_pst'])

    ### BLOCK
    return

    # Move
    write_log(config, "- Done -", stdout=True)
    write_log(config, f"Moving {config['intermediate']['unpacked_pst']} to {config['output_folder']}", stdout=True)
    shutil.move(config['intermediate']['unpacked_pst'], config['output_folder'])
    write_log(config, "===============================================", stdout=True)


# Main program
def main(config: dict) -> None:
    # Is PST file unpacking requested?
    if config['input']['unpack_pst']:
        # Phase 1: unpacking PST
        phase1_unpack_pst_into_directory(config)

        if config['intermediate']['stop_after_unpack']:
            write_log(config, f"Stop after unpack. Unpack location is: {config['intermediate']['unpacked_pst']}", stdout=True)
            return # Return directly, do not clean up.
    else:
        write_log(config, f"Override: Skipping the readpst processing. Pre-unpacked directory is \"{config['intermediate']['unpacked_pst']}\" and continueing", stdout=True)


    # Phase 2: process unpacked directory
    results = phase2_process_and_filter_unpacked_dir(config)

    # Phase 3: summary and clean up
    phase3_summary_and_clean_up(config, results)


# Start
if __name__ == "__main__":
    # Gebruik bijvoorbeeld Europe/Amsterdam als tijdzone
    tz_name = get_localzone_name()
    tz = pytz.timezone(tz_name)
    now = datetime.now(tz)

    # Print in volledig ISO 8601 formaat
    print("Start tijd:", now.isoformat(), now.strftime("%d-%m-%Y %H:%M:%S %Z%z"))

    # Setup all the things
    config = setup()

    try:
        # Open logfile
        if config['run']['logfile']:
            config = open_log_file(config)
            print(f"Logfile opened. Logging will continue in file \"{config['run']['logfile']}\"")
            write_log(config, "========= Logging started =========")

        # Kick it off
        main(config)

    # Close logfile
    finally:
        close_log_file(config)