import json
import pathlib
import hashlib
import fnmatch
import zipfile
import os
import time
import requests
import concurrent.futures
from collections import defaultdict

# Program to search recursively through a given directory,
# calculate MD5 hashes for each file, and send requests to a remote server.
# The server responds if a file is considered suspicious.
# All suspicious files are archived and listed in a JSON output file.


# Function to calculate MD5 hash of a file
def calculate_md5(file_path):
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hasher.update(chunk)
    return hasher.hexdigest()


# Function to recursively list all files from a given directory
def list_recursively(path, file_list):
    for entry in os.listdir(path):
        full_path = os.path.join(path, entry)
        if os.path.isdir(full_path):
            list_recursively(full_path, file_list)
        else:
            file_list.append(full_path)


# Function to check a single file by sending it to the server
def check_file_with_server(file_path):
    md5_hash = calculate_md5(file_path)
    filename = os.path.basename(file_path)

    payload = {"md5": md5_hash, "filename": filename}

    try:
        # Send POST request to the Flask server
        response = requests.post("http://127.0.0.1:5000/check", json=payload, timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result.get("suspicious"):
                return file_path
    except Exception as e:
        print(f"Error while checking file {file_path}: {e}")
    return None


# Load input data from JSON file
with open('script_input.json', 'r') as file:
    data = json.load(file)
    hashes = data.get('md5_hashes', {})
    filenames = data.get('file_patterns', [])


# Start recursive searching from the specified directory
root_dir = '/home/iuliamitisor/test_dir/2xrFy/'
all_files = []
list_recursively(root_dir, all_files)
suspicious_files = []

# Use multiple threads to check files in parallel
# Each thread calculates MD5 and sends an HTTP request
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    for result in executor.map(check_file_with_server, all_files):
        if result:
            suspicious_files.append(result)

# Create a ZIP archive containing the found files
with zipfile.ZipFile('collected_files.zip', 'w') as zipf:
    for file in suspicious_files:
        zipf.write(file)

filedata = defaultdict(list)

# Collect file information and group by MD5 hash
for file in suspicious_files:
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

print("Suspicious files collected and written to filedata.json")
