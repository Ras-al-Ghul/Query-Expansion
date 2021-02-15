from sklearn.feature_extraction.text import TfidfVectorizer

from .search_scrape import remove_punctuation_listify

class Index:

	def __init__(self, result, query, eliminated_words):
		self.data = result
		self.query = query
		
		self.vocab = set()
		self.build_vocab()
		# We want to share the vocab across all parts of all documents
		self.vocab = list(self.vocab)

		file = open('stop_words.txt', 'r')
		content = file.read()
		self.stop_words = content.split('\n')
		self.stop_words.extend(eliminated_words)

		self.vectorizer = dict()
		for region in ('title', 'summary', 'content'):
			self.vectorizer[region] = (
				TfidfVectorizer(vocabulary=self.vocab, sublinear_tf=True, stop_words=self.stop_words))
		
		self.string_data = dict()
		for region in ('title', 'summary', 'content'):
			self.string_data[region] = [' '.join(item[region]) for item in self.data]
		
		self.tfidf = dict()
		for region in ('title', 'summary', 'content'):
			self.tfidf[region] = (
				self.vectorizer[region].fit_transform(self.string_data[region]))

	def build_vocab(self):
		for item in self.data:
			for region in ['title', 'summary', 'content']:
				for word in item[region]:
					self.vocab.add(word)
		
		q = remove_punctuation_listify(self.query)
		for word in q:
			self.vocab.add(word)