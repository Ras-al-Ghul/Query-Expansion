import numpy as np

from math import log
from itertools import permutations

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


def order_query(q, bigrams, candidates, iter_no):
	q = q[0].split(' ')
	dupq = q[::]
	dupq = remove_punctuation_listify(dupq)

	if iter_no == 1:
		if len(dupq) >= 2:
			sc1, sc2 = 0, 0
			cur, alt = tuple(dupq[-2:]), tuple(dupq[-2:][::-1])

			if cur in bigrams:
				sc1 += bigrams[cur]
			if alt in bigrams:
				sc2 += bigrams[alt]

			if sc2 > sc1:
				dupq[-2:] = dupq[-2:][::-1]
				q[-2:] = q[-2:][::-1]

	c1, c2, score = candidates[0], candidates[1], 0

	for pair in list(permutations(range(len(candidates)), 2)):

		w1, w2 = candidates[pair[0]], candidates[pair[1]]

		sc = 0
		if (dupq[-1], w1) in bigrams:
			sc += bigrams[(dupq[-1], w1)]
		if (w1, w2) in bigrams:
			sc += bigrams[(w1, w2)]

		if sc > score:
			c1, c2 = w1, w2
			score = sc

	q.append(c1)
	q.append(c2)

	return q


def enhance_query(query, results, ind, bigrams, relevant, non_relevant, iter_no):
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

	# words could share the same tfidf score, break ties with bigrams
	vals = []
	for i in ranked_terms[::-1]:
		if new_query_vector[i] not in vals:
			vals.append(new_query_vector[i])
			if len(vals) >= 2:
				break
	
	candidates = []
	for i in ranked_terms[::-1]:
		if new_query_vector[i] in vals:
			candidates.append(ind.vocab[i])
		else:
			break

	temp = [query]
	temp = order_query(temp, bigrams, candidates, iter_no)

	return ' '.join(temp)
