from googleapiclient.discovery import build
from config import search_engine_id, key


def search(query_terms):
    search = build("customsearch", "v1", developerKey=key)

    result = search.cse().list(
        q=query_terms,
        cx=search_engine_id).execute()

    items = result['items']
    prettify_results = [{
        'id': idx,
        'url': item.get('link'),
        'title': item.get('title'),
        'summary': item.get('snippet')}
        for idx, item in enumerate(items)]

    return prettify_results