import os
import codecs
import csv
import json
from bs4 import BeautifulSoup
from src.config import configApp
from concurrent.futures import ProcessPoolExecutor
from queue import Queue


def html_jobs():
    with open(configApp.filename_jobs_html_files) as f:
        reader = csv.reader(f, delimiter=",")
        for row in reader:
            filename = row[0]
            url_site = row[1]
            if os.path.exists(filename):
                with codecs.open(filename, "r", "utf8") as html_file:
                    yield html_file.read(), url_site
#end-def


def job_desc(html):
    soup = BeautifulSoup(html, "html.parser")
    #div = soup.select(".print-container")
    div = soup.select_one(".print-container")
    if not div:
        return ""
    parent = div.parent.parent.parent
    result = parent.find_all(text=True)
    return ' '.join(result)
        #text = div.parent.parent.parent.text
        #if len(text) > 200:
        #    yield text


def clean_text(text, list_chars):
    result = text.replace("\t", " ").replace("\r", " ").replace("\n", " ")
    for char in list_chars:
        result = result.replace(char, " ")
    return result


def words_counting(text):
    after_clean = clean_text(text, [c for c in "„;:.¡!?()/,“…'\"\\"])
    result = {}
    words = after_clean.split(" ")
    for word in words:
        word = word.strip().lower()
        if len(word) > 1:
            result[word] = result.get(word, 0) + 1
    return result


def words_by_jobs_desc(html, url_site):
    return {
        "url": url_site,
        "words": words_counting(job_desc(html))
    }


def merge_dict(list_dict):
    result = {}
    for item_dict in list_dict:
        for key in item_dict["words"].keys():
            result[key] = result.get(key, 0) + item_dict["words"][key]
    return result


def print_csv(list_of_tuple):
    my_list = [f"{word},{count}\n" for word, count in list_of_tuple]
    with codecs.open("commout-out.csv", "w", "utf8") as f:
        f.writelines(["word,count\n"] + my_list)

def main():
    myqueue = Queue()

    def add_result_to_queue(fut, queue):
        aux = fut.result()
        if aux is not None:
            queue.put(aux)

    with ProcessPoolExecutor(max_workers=16) as executor:
        for html, url_site in html_jobs():
            future = executor.submit(words_by_jobs_desc, html, url_site)
            future.add_done_callback(lambda fut: add_result_to_queue(fut, myqueue))
        #end-for

        executor.shutdown()
    #end-with

    data = []
    while not myqueue.empty():
        data.append(myqueue.get())

    #for item in data:
    #    if "rabbitmq" in item["words"]:
    #        print(item["url"])

    #merge_dict(data)
    list_of_tuple = [(k, v) for k, v in merge_dict(data).items()]
    list_of_tuple.sort(key=lambda x: x[1])
    print_csv(list_of_tuple)

if __name__ == '__main__':
    main()