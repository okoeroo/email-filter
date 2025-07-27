import asyncio
import os
import pathlib
from tqdm import tqdm
from tqdm.asyncio import tqdm_asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed

from support.logging import write_log
from support.handleemail import read_eml_async, apply_eml_filters, verdict_eml_filter_output
from support.handleics import read_ics_to_text, apply_ics_filters, verdict_ics_filter_output


# Cleanup a file: meaning, removing a file when, not in debug mode, a match
async def cleanup_file(config: dict, context: dict) -> None:
    if config['generic'].get('dryrun', False):
        return

    # If the match key exists, check the value. If it doesn't exist, it's probably not yet set. Just clean up
    should_remove = ('match' not in context or (not context.get('match')))

    # Don't remove, bail
    if not should_remove:
        return

    # Remove
    if config['generic'].get('verbose', False):
        write_log(config, f"Removing non-match: {context.get('filepath')}")
    await asyncio.to_thread(os.unlink, context['filepath'])    


async def analyse_filetype_eml(config: dict, context: dict) -> dict:
    # Read and parse email
    # context['msg'] = read_eml(context['filepath'])
    context['msg'] = await read_eml_async(context['filepath'])

    # Applying all the filter rules on the email
    context = await apply_eml_filters(config, context)

    # Return verdict value, hit = True, no hit = False
    context['match'] = verdict_eml_filter_output(config, context)

    # Cleanup file, keeping logic into account
    await cleanup_file(config, context)

    return context


async def analyse_filetype_ics(config: dict, context: dict) -> dict:
    try:
        # Read and parse email
        context['gcal_full_text'] = await read_ics_to_text(context['filepath'])

        # When nothing is matching in the ICS file, cleanup the file
        if not context['gcal_full_text']:
            # Cleanup file, keeping logic into account
            write_log(config, f"Warning (analyse_filetype_ics, post read_ics_to_text): \"{context['filepath']}\" could not be parsed or it contained no useful content.")
            await cleanup_file(config, context)
            return None

    except Exception as e:
        write_log(config, f"Error (analyse_filetype_ics, post read_ics_to_text): {e} for file {context['filepath']}")
        return None

    try:
        # Applying all the filter rules on the email
        context = apply_ics_filters(config, context)

        # Return verdict value, hit = True, no hit = False
        context['match'] = verdict_ics_filter_output(context)

        # Cleanup file, keeping logic into account
        await cleanup_file(config, context)

        return context
    except Exception as e:
        write_log(config, f"Error (analyse_filetype_ics): {e} for file {context['filepath']}")
        return None


# analyse .eml
# Each filter replies with a boolean.
# The final decision is a boolean
async def analyse_file(config: dict, filepath: str) -> dict:
    context = {}

    context['filepath'] = filepath
    context['extention'] = pathlib.Path(filepath).suffix.lower()
    match context['extention']:
        case ".ics":
            context['extention'] = context['extention']
            context = await analyse_filetype_ics(config, context)
        case ".eml":
            context['extention'] = context['extention']
            context = await analyse_filetype_eml(config, context)
        case _:
            write_log(config, f"Warning: File extention \"{context['extention']}\" not supported, found in file: {context['filepath']}", level="WARNING")
            context['match'] = False
            await cleanup_file(config, context)

    return context


# count all files
def gather_all_files(root: str):
    for dirpath, _, filenames in os.walk(root):
        for filename in filenames:
            yield os.path.join(dirpath, filename)


async def analyse_wrapper(config, path):
    if config.get('verbose'):
        write_log(config, f'Analysing file: {path}')
    return await analyse_file(config, path)


# def walk_and_analyse(config) -> list:
#     if not os.path.exists(config['intermediate']['unpacked_pst']):
#         raise FileNotFoundError(f"{config['intermediate']['unpacked_pst']} does not exist")

#     write_log(config, f"Info: Gathering files...")
#     files = list(gather_all_files(config['intermediate']['unpacked_pst']))
#     write_log(config, f"Info: List completed with {len(files)} files.")

#     results: list = []

#     with tqdm(files, desc="Processing files", unit="file") as pbar:
#         # for path in pbar:
#         #     context = analyse_wrapper(config, path)
#         #     if context:
#         #         pbar.set_postfix(file=os.path.basename(context['filepath']))
#         #         results.append(context)
#         #     pbar.update(1)

#         # semafoor = True
#         for i, path in enumerate(files, 1):
#             # if semafoor and path == "/Users/okoeroo/Documents/Onderzoeken/WOO/M250411843/OUTPUT-M250411843/RAW/tmpvncdapbo/ministerlzs@minvws.nl/Postvak IN/14950.eml":
#             #     # Fast Forward
#             #     semafoor = False

#             # if semafoor:
#             #     write_log(config, f"Fast forward: {path}")
#             #     pbar.update(1)
#             #     continue


#             if os.path.basename(path) == '24567.eml':
#                 print("this is the problem here")

#             context = analyse_wrapper(config, path)
#             if context:
#                 if os.path.basename(context['filepath']) == '15631.eml':
#                     print("problematic here")

#                 pbar.set_postfix(file=os.path.basename(context['filepath']))
#                 results.append(context)

#             # Per 10
#             # if i % 10 == 0:
#             #     pbar.update(10)
#             pbar.update(1)

#             # Elke 1000 bestanden: toon status
#             if i % 1000 == 0:
#                 print(f"STATUS !!! current: {pbar.n}, total: {pbar.total}, percentage {(pbar.n / pbar.total) * 100:.2f}%")

#     return results

import os
import asyncio
from tqdm.asyncio import tqdm_asyncio

async def walk_and_analyse(config) -> list:
    if not os.path.exists(config['intermediate']['unpacked_pst']):
        raise FileNotFoundError(f"{config['intermediate']['unpacked_pst']} does not exist")

    write_log(config, "Info: Gathering files...")
    files = list(gather_all_files(config['intermediate']['unpacked_pst']))
    write_log(config, f"Info: List completed with {len(files)} files.")

    results = []
    semaphore = asyncio.Semaphore(config['run']['async_parallelism'])  # Max parallelism

    async def process(path):
        async with semaphore:
            if config['generic']['debug']:
                write_log(config, f"Start analysis of \"{path}\"", stdout=True)

            try:
                context = await analyse_wrapper(config, path)
                if context:
                    results.append(context)
            except Exception as e:
                write_log(config, f"Error (post: analyse_wrapper): analysing \"{path}\"", level = "ERROR", stdout=True)


    # Laat tqdm de taken afhandelen inclusief progressbar
    await tqdm_asyncio.gather(*(process(p) for p in files), desc="Processing files", unit="file")

    return results