import os
import tempfile


def create_random_named_directory() -> str:
    temp_dir = tempfile.mkdtemp(dir='/tmp')
    print(f'Randomly named directory created at: {temp_dir}')
    return temp_dir

def remove_empty_dirs(path):
    # Walk the directory from bottom to top
    for root, dirs, files in os.walk(path, topdown=False):
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            # Check if the directory is empty
            if not os.listdir(dir_path):
                print(f"Removing empty directory: {dir_path}")
                os.rmdir(dir_path)    

# Walk dir and start analyses
def remove_files_not_matching_list_of_extentions(start_path: str, allowlisted_extentions: list[str]) -> bool:
    for dirpath, dirnames, filenames in os.walk(start_path):
        for filename in filenames:
            for ext in allowlisted_extentions:
                # if the extention of the file is in the allow list, continue.
                if filename.endswith(ext):
                    continue
                # else the extention is not in the allow list, remove and clean.
                else:
                    filepath = os.path.join(dirpath, filename)
                    print("Removing non .eml file:", filepath)
                    os.unlink(filepath)