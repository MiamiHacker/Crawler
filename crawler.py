#!/usr/bin/env python3

from bs4 import BeautifulSoup
from colorama import Fore
import requests
import requests.exceptions
import urllib.parse
from collections import deque
import re

login_scan = True

#target_url = str(input('[+] Enter Target URL To Scan: '))
target_url = 'http://192.168.2.7/'
# target_url = 'http://192.168.2.7/wp-login.php?'

urls = deque([target_url])

founded_urls = set()
founded_emails = set()
founded_logins = set()

#set the maximum scan 
maxScans = 70
count = 0

j = 0
try:
    while len(urls):
        j += 1
        count += 1
        if count == maxScans:
            break
        url = urls.popleft()
        founded_urls.add(url)

        founded_parts = urllib.parse.urlsplit(url)
        if "/wp-login.php" in url and login_scan:
            with open("login.txt", "a+") as file:
                file.seek(0) 
                lines = file.read().splitlines() 
                value = url
                if value in lines:
                    # print()
                    pass
                else:
                    # write to file
                    wr_value = value
                    file.write(wr_value + "\n") # in append mode writes will always go to the end, so no need to seek() here
                    print(Fore.YELLOW, "New loginpage stored:", Fore.GREEN, (url), Fore.RESET)

        base_url = '{0.scheme}://{0.netloc}'.format(founded_parts)
        path = url[:url.rfind('/')+1] if '/' in founded_parts.path else url
 
        print (Fore.RESET + '[%d] Crawling %s' % (count, url))
        try:
            response = requests.get(url)
        except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError):
            continue

        new_emails = set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", response.text, re.I))
        founded_emails.update(new_emails)
        
        new_login = set(re.findall(r"[a-z0-9\.\-+_]+login[a-z0-9\.\-+_]+\.[a-z]+", response.text, re.I))
        founded_logins.update(new_login)
        
        soup = BeautifulSoup(response.text, features="lxml")
        for anchor in soup.find_all("a"):
            link = anchor.attrs['href'] if 'href' in anchor.attrs else ''
            if link.startswith('/'):
                link = base_url + link
            elif not link.startswith('http'):
                link = path + link
            if not link in urls and not link in founded_urls:
                urls.append(link)

        for mail in founded_emails:
            value = mail
            with open("mail.txt", "a+") as file:
                file.seek(0) # set position to start of file
                lines = file.read().splitlines() # now we won't have those newlines
                if value in lines:
                    # print()
                    pass
                else:
                    wr_value = value
                    file.write(wr_value + "\n") # in append mode writes will always go to the end, so no need to seek() here
                    print(Fore.YELLOW, "New MailAddress stored:", Fore.GREEN, (mail), Fore.RESET)

except KeyboardInterrupt:
    print('[-] Closing!')
