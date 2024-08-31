import sys
import subprocess


def run_readpst(output_dir: str, input_filepath: str):
    process = subprocess.Popen(['readpst', '-j', '8', '-D', '-e', '-o', output_dir, input_filepath], 
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Print stdout in real time
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print(output.strip())

    # Print stderr in real time
    while True:
        error = process.stderr.readline()
        if error == '' and process.poll() is not None:
            break
        if error:
            print(error.strip(), file=sys.stderr)

    # Wait for the process to complete and get the return code
    process.wait()
    return_code = process.returncode
    print("Return code", return_code)
    return return_code