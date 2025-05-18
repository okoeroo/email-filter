import os
import sys
import subprocess
from support.logging import write_log


def run_readpst(config: dict) -> None:
    output_dir: str = config['tmp_pst_dir']
    input_filepath: str = config['input_pst_path']

    # Bestaat het?
    if not os.path.exists(input_filepath):
        raise FileNotFoundError(f"PST niet gevonden: {input_filepath}")

    # Run
    process = subprocess.Popen(['readpst', '-b', '-j', '8', '-D', '-e', '-o', output_dir, input_filepath], 
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

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