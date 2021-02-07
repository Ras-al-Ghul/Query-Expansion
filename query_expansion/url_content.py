import requests
from bs4 import BeautifulSoup
from multiprocessing.dummy import Pool as ThreadPool


def get_document_content(url):

    html_doc = requests.get(url).text

    soup = BeautifulSoup(html_doc, 'html.parser')
    data = soup.findAll('p')
    data = [p.get_text().replace('\n', '').replace('\t', '') for p in data]

    return data


def extract_content(results):

    def find_content(result):
        result["content"] = get_document_content(result['url'])

    with ThreadPool(processes=10) as pool:
        for result in results:
            pool.apply_async(find_content, args=(result,))

        pool.close()
        pool.join()
