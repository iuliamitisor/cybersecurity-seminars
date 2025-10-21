import json
import pathlib
import hashlib
import fnmatch
import zipfile
import os
from collections import defaultdict
import time

# Program to search for files matching given names or MD5 hashes,
# collect their information, archive them into a ZIP file
# and write the collected file information to a JSON file.

# Function to calculate MD5 hash of a file
def calculate_md5(file_path):
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hasher.update(chunk)
    return hasher.hexdigest()

# Function to recursively list from directories the files which
# match given filenames or have given MD5 hashes 
printed_files = []
def list_recursively(path, filenames, hashes, printed_files):
    for entry in os.listdir(path):
        if os.path.isdir(os.path.join(path, entry)):
            list_recursively(os.path.join(path, entry), filenames, hashes, printed_files)
        elif calculate_md5(os.path.join(path, entry)) in hashes:
            printed_files.append(os.path.join(path, entry))
        else:
            for filename in filenames:
                if fnmatch.fnmatch(entry, filename):
                    full_path = os.path.join(path, entry)
                    if os.path.isdir(full_path):
                        list_recursively(full_path, filenames, hashes, printed_files)
                    else:
                        printed_files.append(full_path)
            

# Load input data from JSON file
with open('script_input.json', 'r') as file:
    data = json.load(file)
    hashes = data.get('md5_hashes', {})
    filenames = data.get('file_patterns', [])


# Start recursive searching from the specified directory
list_recursively('/home/iuliamitisor/test_dir', filenames, hashes, printed_files)
print(printed_files)

# Create a ZIP archive containing the found files
with zipfile.ZipFile('collected_files.zip', 'w') as zipf:
    for file in printed_files:
        zipf.write(file)

filedata = defaultdict(list)

# Collect file information and group by MD5 hash
for file in printed_files:

    # Store only the relative path to test_dir
    rel_path = os.path.relpath(file, '/home/iuliamitisor')
    file_info = {
        'file_path': rel_path,
        'last_modified': time.ctime(os.path.getmtime(file))
    }
    filedata[calculate_md5(file)].append(file_info)

# Write to JSON output file
json_str = json.dumps(filedata, indent=4)
with open("filedata.json", "w") as f:
    f.write(json_str)