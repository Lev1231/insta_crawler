import requests
from bs4 import BeautifulSoup

def main(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'xml')
    print (r.content)
    usernames = [item.text for item in soup.find_all('instagramUsername')]

    return usernames

if __name__ == "__main__":
    url = "https://buzzbooker.info/wp-content/uploads/wpallexport/exports/c6ee53c0f95e394299ad9956d700ed61/usernames.xml"
    main(url)