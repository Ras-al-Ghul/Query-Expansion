from googleapiclient.discovery import build


def google_query(query_terms):
    search = build("customsearch", "v1", developerKey="AIzaSyAENB1D2LxKbqSmJqdRSKaRVT67_XSKJ_c");

    result = search.cse().list(
        q=query_terms,
        cx="14e471d67764dc04d").execute()

    items = result['items']
    prettify_results = [{
        'id': idx,
        'url': item.get('link'),
        'title': item.get('title'),
        'summary': item.get('snippet')}
        for idx, item in enumerate(items)]

    return prettify_results