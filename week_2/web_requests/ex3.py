import requests
import bs4
import os
import hashlib

# Program to download all images from a web page and
# print all external links.

url = 'https://www.python.org/'

# Create directory to store file caches
os.makedirs('caches', exist_ok=True)

# Compute md5 hash for a given URL to use as cache filename
def get_cache_filename(url):
    url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
    return os.path.join('caches', url_hash)

def fetch_url(url, binary=False):
    cache_file = get_cache_filename(url)

    # If cached file already exists, read from it
    if os.path.exists(cache_file):
        if binary:
            mode = 'rb'
        else:
            mode = 'r'
        with open(cache_file, mode) as f:
            return f.read()

    # If not cached, request the URL and cache the response
    response = requests.get(url)
    response.raise_for_status()
    data = response.content if binary else response.text

    if binary:
        mode = 'wb'
    else:
        mode = 'w'    
    with open(cache_file, mode, encoding=None if binary else 'utf-8') as f:
        f.write(data)

    # Return data either binary or text
    return data

content = bs4.BeautifulSoup(fetch_url(url), 'html.parser')

# Create a directory for images
os.makedirs('images', exist_ok=True)

# Find all elements with img tag
for img in content.find_all('img'):
    img_url = img.get('src')
    # If img url is relative, make it absolute and request the image
    if not img_url.startswith('http'):
        img_url = requests.compat.urljoin(url, img_url)
    img_data = fetch_url(img_url, binary=True)
    filename = os.path.join('images', os.path.basename(img_url))
    with open(filename, 'wb') as imagefile:
        imagefile.write(img_data)

# Print all external links
for link in content.find_all('a', href=True):
    # Extract link href, if not from python.org, print it
    href = link['href']
    if 'python.org' not in href and href.startswith('http'):
        print(href)
