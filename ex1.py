import subprocess
import csv
import re
import datetime
from collections import defaultdict

# Program to extract SSH logs, identify IP addresses, first and last 
# appearance dates, and write the data to a CSV file.


# Run the command to extract SSH logs
print(subprocess.run("journalctl -u ssh > file.txt", shell=True))
log_dict = defaultdict(list)
ips = []

# Read the log file and extract dates and IP addresses
with open("file.txt") as textfile:
    for line in textfile:
        pattern = re.compile(
            r"^([A-Z][a-z]{2}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}).*?\b(\d{1,3}(?:\.\d{1,3}){3})\b"
        )

        # Match the line against regex and extract data into dictionary
        match = pattern.search(line)
        if match:
            date, ip = match.groups()
            if ip not in ips:
                ips.append(ip)
            log_dict[ip].append(date)

# Define fields for CSV
fields = ["ip", "apparition_no", 'date_first', "date_last"]

# Write the extracted data to a CSV file
with open("file.csv", "w") as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(fields)
    for ip in ips:
        fields = [ip, len(log_dict[ip]), log_dict[ip][0], log_dict[ip][len(log_dict[ip]) - 1]]
        csvwriter.writerow(fields)
