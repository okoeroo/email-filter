import os
import sys
import subprocess
from support.logging import write_log


def run_readpst(config: dict) -> None:
    input_filepath: str = config['input']['input_pst_path']
    output_dir: str = config['intermediate']['unpacked_pst']
    run_cmd_list = ['readpst', '-b', '-j', str(config['run']['threads']), '-D', '-e', '-o', output_dir, input_filepath]

    # Bestaat het?
    if not os.path.exists(input_filepath):
        raise FileNotFoundError(f"PST file niet gevonden: {input_filepath}")

    if not os.path.exists(output_dir):
        raise FileNotFoundError(f"Output path niet beschikbaar: {output_dir}")



    if not config['generic']['verbose'] and not config['generic']['debug']:
        write_log(config, f"Starting readpst run", stdout=True)
    else:
        write_log(config, f"Starting readpst run: {" ".join(run_cmd_list)}", stdout=True)


    # Run
    process = subprocess.Popen(run_cmd_list,
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE, 
                               text=True)

    # Print stdout in real time
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            write_log(config, output.strip(), stdout=True)

    # Print stderr in real time
    while True:
        error = process.stderr.readline()
        if error == '' and process.poll() is not None:
            break
        if error:
            write_log(config, error.strip(), level="ERROR", stdout=True)

    # Wait for the process to complete and get the return code
    process.wait()
    return_code = process.returncode

    if return_code != 0:
        raise Exception("readpst failed with error core {return_code}")

    write_log(config, f"readpst return code: {return_code}", stdout=True)