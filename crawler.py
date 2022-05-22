from bs4 import BeautifulSoup
from colorama import Fore
import requests
import requests.exceptions
import urllib.parse
from collections import deque
import re

target_url = str(input('[+] Enter Target URL To Scan: '))
urls = deque([target_url])

founded_urls = set()
founded_emails = set()
#set the maximum scan 
maxScans = 25
count = 0
try:
    while len(urls):
        count += 1
        if count == maxScans:
            break
        url = urls.popleft()
        founded_urls.add(url)

        founded_parts = urllib.parse.urlsplit(url)
        base_url = '{0.scheme}://{0.netloc}'.format(founded_parts)

        path = url[:url.rfind('/')+1] if '/' in founded_parts.path else url

        print (Fore.RESET + '[%d] Crawling %s' % (count, url))
        try:
            response = requests.get(url)
        except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError):
            continue

        new_emails = set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", response.text, re.I))
        founded_emails.update(new_emails)

        soup = BeautifulSoup(response.text, features="lxml")

        for anchor in soup.find_all("a"):
            link = anchor.attrs['href'] if 'href' in anchor.attrs else ''
            if link.startswith('/'):
                link = base_url + link
            elif not link.startswith('http'):
                link = path + link
            if not link in urls and not link in founded_urls:
                urls.append(link)
except KeyboardInterrupt:
    print('[-] Closing!')

for mail in founded_emails:
    print(Fore.YELLOW + "Founded:", mail)
