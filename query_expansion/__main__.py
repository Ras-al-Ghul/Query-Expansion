import sys
import threading
import pickle

from copy import deepcopy

from . import rocchio
from . import search_scrape as sc
from .indexer import Index


def main():
    if len(sys.argv) < 3:
        print("python3 -m query_expansion <query> <precision>")
        print("query - string you start searching with")
        print("precision - must be a float value between 0 and 1")
        return
    else:
        query = sys.argv[1]
        expected_precision = float(sys.argv[2])
        if expected_precision > 1 or expected_precision < 0:
            print("precision - must be a float value between 0 and 1")
            return

    cur_precision = 0.
    
    while cur_precision < expected_precision:
        print("query ", query)
        results = sc.search(query)
        # with open("/home/dipankar/Desktop/Query-Expansion/query_expansion/elonmusk.pkl", "rb") as fp:
        #     results = pickle.load(fp)

        if len(results) < 10:
            print("Too few relevant results, quitting")
            break

        relevant_documents, non_relevant_documents = [], []

        res = deepcopy(results)
        t1 = threading.Thread(target=sc.get_feedback, 
                args=(res, relevant_documents, non_relevant_documents,))
        t2 = threading.Thread(target=sc.extract_content,
                args=(results,))
        t1.start()
        t2.start()
        t2.join()

        t3 = threading.Thread(target=sc.process_input,
                args=(results,))
        t3.start()
        t3.join()
        t1.join()

        cur_precision = len(relevant_documents)/len(results)
        if cur_precision == 0:
            print("Precision is 0., quitting")
            break

        print("Precision: ", cur_precision)
        if cur_precision >= expected_precision:
            break

        # At this point, result is a list of 10 entries, with each entry having
        # an id, url, title, summary, and content
        # Each of title, summary, content is list of lowercase strings
        # print(results[0])

        ind = Index(results, query)
        query = rocchio.enhance_query(
            query, results, ind, relevant_documents, non_relevant_documents)
    

if __name__ == '__main__':
    main()