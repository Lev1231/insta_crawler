import os
import unicodecsv as csv
import requests
import urllib2
from bs4 import BeautifulSoup

import config

def row_to_csv(file, row):
    if not os.path.exists(file):
        with open(file, 'wb') as f:
            writer = csv.writer(f)
            writer.writerow(row)
    else:
        with open(file, 'ab') as f:
            writer = csv.writer(f)
            writer.writerow(row)

def main():
    s = requests.session()
    data = {
        'password_protected_pwd': config.password,
        'wp-submit': 'Log In',
        'testcookie': '1',
        'password-protected': 'login',
        'redirect_to': 'http://139.59.242.156/'
    }
    r = s.post(login_url, data=data)

    page = 228
    while True:
        print (page)
        r = s.get(page_url%page)
        if r.status_code != 200:
            break

        soup = BeautifulSoup(r.content, "html.parser")
        usernames = [x.text.strip() for x in soup.find_all(attrs={'class': 'field field-username'})]
        for username in usernames:
            row_to_csv(output_csv, [username, '0'])

        page += 1

if __name__ == "__main__":
    url = "http://139.59.242.156"
    login_url = "http://139.59.242.156/?password-protected=login"
    page_url = "http://139.59.242.156/page/%d/?s&wpsolr_fq[0]=region_str:Japan&wpsolr_sort=followers_str_desc"

    head = ['username', 'status']
    output_csv = "japan_username.csv"

    if not os.path.exists(output_csv):
        row_to_csv(output_csv, head)


    # print (urllib2.unquote(page_url))
    main()