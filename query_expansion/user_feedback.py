from pprint import pprint

def get_feedback(search_result):
    relevant_documents = []
    non_relevant_document = []
    for item in search_result:
        pprint(item)
        while True:
            relevant = input("Relevant? (y/n)")
            if relevant == 'y':
                relevant_documents.append(item)
                break
            elif relevant == 'n':
                non_relevant_document.append(item)
                break
            else:
                print('Invalid input, please enter (y/n)')

    return relevant_documents, non_relevant_document