import sys
from query_expansion import google_api as google
from query_expansion import user_feedback as user


def main():
    if len(sys.argv) < 3:
        print("python -m query_expansion <query> <precision>")
        print("query - string you start searching with.")
        print("precision - must be a float value between 0 and 1")
        return
    else:
        query = sys.argv[1]
        expected_precision = float(sys.argv[2])
        if expected_precision>1 or expected_precision<0:
            print("precision - must be a float value between 0 and 1")
            return

    results = google.search(query)
    relevant_documents, non_relevant_documents = user.get_feedback(results)
    #print(relevant_documents, non_relevant_documents)


if __name__ == '__main__':
    main()