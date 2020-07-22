import requests
from concurrent.futures import ProcessPoolExecutor


class Page:
    url = ""
    filename = ""


class Downloader:

    def __init__(self, parallel):
        self.parallel = parallel
        self.pending_download = 0

    def save(self, my_list: list):
        self.pending_download = len(my_list)
        with ProcessPoolExecutor(max_workers=self.parallel) as executor:

            for page in my_list:
                future = executor.submit(self._make_get_request, page.url, page.filename)
                future.add_done_callback(lambda fut: self._save_file(fut.result()))
            executor.shutdown()

    @staticmethod
    def _make_get_request(url, filename):
        try:
            rs = requests.get(url)
            if rs.status_code != 200:
                print(f"status code = {rs.status_code} for {url}")
                return False
            return (rs.content, filename)
        except Exception as ex:
            print(f"at {url}",ex)
            return False

    def _save_file(self, content):
        self.pending_download -= 1
        print("pending download:", self.pending_download)
        if not content:
            return
        filename = content[1]
        with open(filename, "wb") as f:
            f.write(content[0])

