import requests
import re

from bs4 import BeautifulSoup
from multiprocessing.dummy import Pool as ThreadPool
from googleapiclient.discovery import build

from .config import search_engine_id, key
from pprint import pprint


# Send query and get results from Google API
def search(query_terms):
    search_result = build("customsearch", "v1", developerKey=key)

    result = search_result.cse().list(
                q=query_terms,
                cx=search_engine_id).execute()

    items = result['items']
    pretty_results = [{
        'id': idx,
        'url': item.get('link') if item.get('link') is not None else '',
        'title': item.get('title') if item.get('title') is not None else '',
        'summary': item.get('snippet') if item.get('snippet') is not None else ''}
        for idx, item in enumerate(items)]

    return pretty_results


# Helper to scrape the URL to get content
def get_document_content(url):
    data = []
    try:
        html_doc = requests.get(url, timeout=1).text

        soup = BeautifulSoup(html_doc, 'html.parser')
        data = soup.findAll('p')
        data = [p.get_text().replace('\n', '').replace('\t', '') for p in data]
    except:
        # timeout exception if resutls are not fetched
        pass
    return data


# Extract content from webpages
def extract_content(results):

    def find_content(result):
        result["content"] = get_document_content(result['url'])

    with ThreadPool(processes=10) as pool:
        for result in results:
            pool.apply_async(find_content, args=(result,))

        pool.close()
        pool.join()


# Display results to user and get feedback
def get_feedback(search_result, relevant_documents, non_relevant_documents):
    for item in search_result:
        pprint(item)
        while True:
            relevant = input("Relevant? (y/n)")
            if relevant == 'y':
                relevant_documents.append(item['id'])
                break
            elif relevant == 'n':
                non_relevant_documents.append(item['id'])
                break
            else:
                print('Invalid input, please enter (y/n)')


# Remove punctuations and convert to a single list of words
def remove_punctuation_listify(ip):
    if not isinstance(ip, list):
        ip = [ip]

    tmp = [re.split('\W+', item) for item in ip]

    res = []
    for itm in tmp:
        for word in itm:
            if word != '':
                res.append(word.lower())

    return res


# Process each section in each result to contain a list of words
def process_input(res_list):
    for item in res_list:
        res = []
        for k in ('title', 'summary', 'content'):
            if item[k] != []:
                item[k] = remove_punctuation_listify(item[k])


# Extract bigrams from results
def get_bigrams(res_list, bigrams):
    for item in res_list:
        for k in ('title', 'summary', 'content'):
            if item[k] != []:
                for i in range(len(item[k])-1):
                    bigrams[(item[k][i], item[k][i+1])] += 1
