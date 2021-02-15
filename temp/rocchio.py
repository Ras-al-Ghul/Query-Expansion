import numpy as np

from math import log

from .config import (ALPHA, BETA, GAMMA, 
					 TITLE, SUMMARY, CONTENT)
from .search_scrape import remove_punctuation_listify


def compute_document_weighted_vector(ind):
	doc_weighted_vectors = np.zeros((10, len(ind.vocab)))

	for region, weight in zip(['title', 'summary', 'content'],
							  [TITLE, SUMMARY, CONTENT]):

		for i in range(10):
			doc_weighted_vectors[i][:] += (weight*ind.tfidf[region][i][:])

	return doc_weighted_vectors


def compute_query_vector(q, ind):
	query_vector = np.zeros(len(ind.vocab))
	
	for word in q:
		if word in ind.vectorizer['content'].vocabulary_:
			index = ind.vectorizer['content'].vocabulary_[word]
			query_vector[index] = (log(1 + q.count(word), 10) * 
								   ind.vectorizer['content'].idf_[index])

	norm = np.linalg.norm(query_vector)
	if norm != 0:
		query_vector /= norm

	return query_vector


def order_query(q, bigrams):
	dupq = q[::][-3:]
	dupq = remove_punctuation_listify(dupq)

	sc1, sc2 = 0, 0

	if (dupq[0], dupq[1]) in bigrams:
		sc1 += bigrams[(dupq[0], dupq[1])]
	if (dupq[1], dupq[2]) in bigrams:
		sc1 += bigrams[(dupq[1], dupq[2])]
	
	if (dupq[0], dupq[2]) in bigrams:
		sc1 += bigrams[(dupq[0], dupq[2])]
	if (dupq[2], dupq[1]) in bigrams:
		sc1 += bigrams[(dupq[2], dupq[1])]

	if sc1 < sc2:
		q[-2:0] = q[-2:0][::-1]

	return q


def enhance_query(query, results, ind, bigrams, relevant, non_relevant):
	document_vectors = compute_document_weighted_vector(ind)
	q = remove_punctuation_listify(query)
	query_vector = compute_query_vector(q, ind)
	
	new_query_vector = (ALPHA * query_vector)

	for doc_id in relevant:
		new_query_vector += ((BETA/len(relevant)) * document_vectors[doc_id][:])

	for doc_id in non_relevant:
		new_query_vector -= ((GAMMA/len(non_relevant)) * document_vectors[doc_id][:])

	new_query_vector = new_query_vector.clip(min=0)

	ranked_terms = list(np.argsort(new_query_vector))
	# remove query words from future choices
	for word in q:
		ranked_terms.remove(ind.vectorizer['content'].vocabulary_[word])

	temp = [query]
	print([(ind.vocab[index], new_query_vector[index]) for index in ranked_terms[-20:][::-1]])
	temp.extend([ind.vocab[index] for index in ranked_terms[-2:][::-1]])
	temp = order_query(temp, bigrams)

	return ' '.join(temp)
