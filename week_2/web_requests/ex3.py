import requests
import bs4
import os

# Program to download all images from a web page and
# print all external links.

url = 'https://www.python.org/'
response = requests.get(url)
content = bs4.BeautifulSoup(response.text, 'html.parser')

# Create a directory for images
os.mkdir('images')

# Find all elements with img tag
for img in content.find_all('img'):
    img_url = img.get('src')
    # If img url is relative, make it absolute and request the image
    if not img_url.startswith('http'):
        img_url = requests.compat.urljoin(url, img_url)
    img_data = requests.get(img_url).content
    filename = os.path.join('images', os.path.basename(img_url))
    with open(filename, 'wb') as imagefile:
        imagefile.write(img_data)

# Print all external links
for link in content.find_all('a', href=True):
    # Extract link href, if not from python.org, print it
    href = link['href']
    if 'python.org' not in href and href.startswith('http'):
        print(href)
