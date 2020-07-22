import os
import uuid
import codecs
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from src.config import configApp
from client import Page, Downloader


def create_dir():
    print(configApp.out_dir_job_pages)
    dir_path = configApp.out_dir_job_pages
    os.makedirs(dir_path, exist_ok=True)


def iter_nav_pages():
    for filename in os.listdir(configApp.out_dir_navigation_pages):
        abspath = os.path.join(configApp.out_dir_navigation_pages, filename)
        with codecs.open(abspath, "r", "utf8") as f:
            yield f.read()


def iter_jobs_url():
    parsed_uri = urlparse(configApp.first_navigation_page)
    base_url = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)

    for html in iter_nav_pages():
        soup = BeautifulSoup(html, "html.parser")
        for link in soup.select("div.jobtitle a"):
            aux = link.get("href")
            if aux:
                yield urljoin(base_url, aux)


def create_page_from_url(url):
    filename = str(uuid.uuid1()) + ".html"
    p = Page()
    p.filename = os.path.join(configApp.out_dir_job_pages, filename)
    p.url = url
    return p


def create_downloaded_file(my_list: list):
    with open(configApp.filename_jobs_html_files, "w") as f:
        for page in my_list:
            line = f"{page.filename},{page.url}\n"
            f.write(line)


def main():
    create_dir()
    data = list(map(create_page_from_url, iter_jobs_url()))
    create_downloaded_file(data)

    downloader = Downloader(16)
    downloader.save(data)


if __name__ == '__main__':
    main()
