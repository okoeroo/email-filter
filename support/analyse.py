import os
import pathlib
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

from support.handleemail import read_eml, apply_eml_filters, verdict_eml_filter_output
from support.handleics import read_ics, apply_ics_filters, verdict_ics_filter_output


# Cleanup a file: meaning, removing a file when, not in debug mode, a match
def cleanup_file(config: dict, context: dict) -> None:
    # When not in debug mode, and no match, then remove the file
    if not config['debug'] and not context['match']:
        if config['verbose']:
            print(f"Removing non-match: {context['filepath']}")
        os.unlink(context['filepath'])


def analyse_filetype_eml(config: dict, context: dict) -> dict:
    # Read and parse email
    context['msg'] = read_eml(context['filepath'])

    # Applying all the filter rules on the email
    context = apply_eml_filters(config, context)

    # Return verdict value, hit = True, no hit = False
    context['match'] = verdict_eml_filter_output(config, context)

    # Cleanup file, keeping logic into account
    cleanup_file(config, context)

    return context


def analyse_filetype_ics(config: dict, context: dict) -> dict:
    # Read and parse email
    context['gcal'] = read_ics(context['filepath'])

    # Applying all the filter rules on the email
    context = apply_ics_filters(config, context)

    # Return verdict value, hit = True, no hit = False
    context['match'] = verdict_ics_filter_output(context)

    # Cleanup file, keeping logic into account
    cleanup_file(config, context)

    return context


# analyse .eml
# Each filter replies with a boolean.
# The final decision is a boolean
def analyse_file(config: dict, filepath: str) -> dict:
    context = {}

    context['filepath'] = filepath
    context['extention'] = pathlib.Path(filepath).suffix.lower()
    match context['extention']:
        case ".ics":
            context['extention'] = context['extention']
            context = analyse_filetype_ics(config, context)
        case ".eml":
            context['extention'] = context['extention']
            context = analyse_filetype_eml(config, context)
        case _:
            print(f"Warning: File extention \"{context['extention']}\" not supported, found in file: {context['filepath']}")
            context['match'] = False
            cleanup_file(config, context)

    return context


# count all files
def gather_all_files(root: str):
    for dirpath, _, filenames in os.walk(root):
        for filename in filenames:
            yield os.path.join(dirpath, filename)


# Wrapper zodat tqdm in parallel gebruikt kan worden
def analyse_wrapper(args):
    config, path = args
    if config['verbose']:
        print(f'Analysing file: {path}')
    context = analyse_file(config, path)
    return context


# Walk dir and start analyses
def walk_and_analyse(config) -> None:
    if not os.path.exists(config['tmp_pst_dir']):
        raise FileNotFoundError(f"{config['tmp_pst_dir']} does not exist")

    print(f"Info: Gathering files...")
    files = list(gather_all_files(config['tmp_pst_dir']))
    print(f"Info: List completed with {len(files)} files.")

    results = []

    with ThreadPoolExecutor(max_workers=config.get('threads', 8)) as executor:
        tasks = [(config, path) for path in files]
        futures = {executor.submit(analyse_wrapper, task): task[1] for task in tasks}

        with tqdm(total=len(futures), desc="Processing files", unit="file") as pbar:
            for future in as_completed(futures):
                context = future.result()
                pbar.set_postfix(file=os.path.basename(context['filepath']))
                if context:
                    results.append(context)
                pbar.update(1)
    
    # Samenvatting
    print("\n=== Analyses of files ===")
    cnt = 0
    for context in results:
        if not context['match']:
            continue

        cnt += 1
        print(f"{cnt}: \"{os.path.basename(context['filepath'])}\"")
    