from sklearn.feature_extraction.text import TfidfVectorizer

from .search_scrape import remove_punctuation_listify

class Index:

	def __init__(self, result, query, eliminated_words):
		self.data = result
		self.query = query
		self.regions = ('title', 'summary', 'content')
		
		with open('stop_words.txt', 'r') as f:
			self.stop_words = f.readlines()
		self.stop_words.extend(eliminated_words)
		self.stop_words = remove_punctuation_listify(self.stop_words)

		self.vocab = set()
		self.build_vocab()
		# We want to share the vocab across all parts of all documents
		self.vocab = list(self.vocab)

		self.vectorizer = dict()
		self.string_data = dict()
		self.tfidf = dict()

		self.create_tfidf_vecs()

	def build_vocab(self):
		for item in self.data:
			for region in ['title', 'summary', 'content']:
				for word in item[region]:
					if word not in self.stop_words:
						self.vocab.add(word)
		
		q = remove_punctuation_listify(self.query)
		for word in q:
			if q not in self.stop_words:
				self.vocab.add(word)

	def create_tfidf_vecs(self):
		for region in self.regions:
			self.vectorizer[region] = (
				TfidfVectorizer(stop_words=self.stop_words, vocabulary=self.vocab, 
								sublinear_tf=True))
		
		for region in self.regions:
			self.string_data[region] = [' '.join(item[region]) for item in self.data]
		
		for region in self.regions:
			self.tfidf[region] = (
				self.vectorizer[region].fit_transform(self.string_data[region]))
