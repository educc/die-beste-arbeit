# -----------------------------------------------------------
# This python script download each navigation page starting
# with the url configured in the "application.json" with
# the "firstNavigationPage" property.
# Continuous downloading until the script found the phrase
# "No jobs found" in the html content.
#
# (C) 2020 edu
# -----------------------------------------------------------
import requests
import os
import re
import uuid
from src.config import configApp


class UrlIterator:

    TOKEN = "currentPage%5D=\\d+&"

    def __init__(self, base_url):
        self.base_url = base_url
        self.first_time = True

    def __iter__(self):
        return self

    def __next__(self):
        if self.first_time:
            self.first_time = False
            return self.base_url

        new = self._make_new_url(self.base_url)
        if not new:
            raise StopIteration
        self.base_url = new
        return new

    def _make_new_url(self, url):
        m = re.search(self.TOKEN, url)
        if not m:
            return None
        extract = m.group(0)
        number = int(re.search("=\\d+", extract).group(0)[1:])
        return url.replace(extract, "currentPage%5D=" + str(number+1) + "&")


def create_dir():
    print(configApp.out_dir_navigation_pages)
    dir_path = configApp.out_dir_navigation_pages
    os.makedirs(dir_path, exist_ok=True)


def write_disk(content):
    filename = os.path.join(configApp.out_dir_navigation_pages, str(uuid.uuid1()) + ".html")
    with open(filename, "wb") as f:
        f.write(content)


def main():
    create_dir()
    url_iter = UrlIterator(configApp.first_navigation_page)
    i = 1
    for url in url_iter:
        print("Downloading", i, url)
        rs = requests.get(url)
        if "No jobs found" in rs.text:
            break
        write_disk(rs.content)
        i += 1


if __name__ == "__main__":
    main()
