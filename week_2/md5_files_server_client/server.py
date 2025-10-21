import json
import time
import random
import threading
from flask import Flask, request, jsonify

# Program that checks incoming files from the client
# against a list of known file name patterns and MD5 hashes.
# The server exposes an HTTP endpoint for the client to query.

# Create Flask application
app = Flask(__name__)

# Load input data from JSON file
with open('script_input.json', 'r') as file:
    data = json.load(file)
    known_hashes = set(data.get('md5_hashes', []))
    known_patterns = set(data.get('file_patterns', []))


# Check if file is suspicious
def check_file(file_md5, filename):
    # Simulate processing time
    time.sleep(random.uniform(1, 3))

    # Check if hash or filename pattern is considered suspicious
    suspicious = (
        file_md5 in known_hashes or
        any(pattern in filename for pattern in known_patterns)
    )

    # Return structured result
    return {
        "filename": filename,
        "md5": file_md5,
        "suspicious": suspicious
    }


# HTTP endpoint to handle client requests
@app.route('/check', methods=['POST'])
def check_endpoint():
    data = request.get_json()
    file_md5 = data.get('md5')
    filename = data.get('filename')

    # Process file and return the result
    result = check_file(file_md5, filename)
    return jsonify(result)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, threaded=True)
