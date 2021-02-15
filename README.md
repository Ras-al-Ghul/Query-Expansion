# Query-Expansion
An implementation of Rochhio's algorithm for Query Expansion (with user relevance feedback)
## Files
<ol>
<li>query_expansion
  <ul>
    <li>__init__.py</li>
    <li>__main__.py</li>
    <li>config.py</li>
    <li>indexer.py</li>
    <li>rocchio.py</li>
    <li>search_scrape.py</li>
  </ul>
</li>
<li>README.md</li>
<li>requirements.txt</li>
<li>setup.py</li>
<li>stop_words.txt</li>
<li>test_queries_transcript.txt</li>
</ol>

## Steps to install and run

<p>Install the rquirements from requirements.txt using the below command.</p>

```
 pip3 install -r requirements.txt
```

<p>Run the program using the following command.</p>

```
python3 -m query_expansion <query> <precision>
```
<p>Where query is a string of words that you want to search and precision is a decimal value. For example,</p>

```
python3 -m query_expansion "this is the query" 0.9
```

## Design

<ol>
<li>search_scrape.py :
   <ul>
    <li>Sends a google query.</li> 
    <li>Extracts the summary, title and contents of the query results.</li>
    <li>Gets user feed back on the document relevance.</li>
    <li>Helpers to process text - lower case, eliminate punctuations, etc. </li>
   </ul>
</li>
<li>indexer.py
  <ul>
    <li>Extracts the vocabulary</li>
    <li>Gets list of stop words from stop_words.txt</li>
    <li>Builds tfidf of the summary, title and content using TfidfVectorizer from scikit-learn.</li>
  </ul>
</li>
<li>rocchio.py
  <ul>
    <li>Uses the tfidf and bigram data and suggests the best words for query expansion</li>
  </ul>
</li>
</ol>

## Algorithm
<p>We use Rocchio algorithm along with a few improvisations for the query expansion. The goal is reach the expected precision@10 of search results with minimum number of query expansions. <a href="https://en.wikipedia.org/wiki/Evaluation_measures_(information_retrieval)#Precision_at_K">Precision</a> is measured as the number of relevant documents seen in the top 10 search results returned by Google.</p>
<ol>
  <li>Rocchio's algorithm is used to rank and extract the words that can be used for the query expansion to obtain better results. Steps:
  <ul>
    <li>Start with the inital query and expected precision.</li>
    <li>Obtain the content of top 10 search results using Google Search API and bs4.</li>
    <li>Get user feedback to find the relevant and non relevant documents/search results.</li>
    <li>Extract the feature vectors of the documents</li>
    <li>Now add the feature vectors of the relevant documents to the query feature vector (both are weighted vectors).</li>
    <li>Subtract the feature vectors (weighted) of the non-relevant documents from the query feature vector.</li>
    <li>Sort and pick the top 2 most relevant words form the above resultant feature vector and add to the query. Reorder if needed, based on bigrams.</li>
    <li>repeat from step 2 with the new query until you reach the desired precision.</li>
  </ul>
  </li>
  <li>We give seperate weights for the words from Summary, Title and Content (scraped using BeautifulSoup) of the results. As summary provided by the Google's results would contain the key words, while forming the feature vectors of each document, we give the highest weightage to the words present in the summary, followed by content and title (which have few words and hence greater chance of error, which would lead to query drift).
  </li>
  <li>We reorder the terms in the query after adding the new terms, using the bigrams generated from the content of the search results. Steps:
    <ul>
      <li>Generate the list of bigrams and their frequency from the content of the search results.</li>
      <li>Generate all permutations of the two possible expansions to the query. If it is the first iteration, we even consider reordering the initial user query. Based on bigram frequencies, choose the best possible ordering from expansion candidates. The candidate words for expansion are the words with the highest vector values given by Rocchio's algorithm - all words with the highest two values are considered.</li>
    </ul>
  </li>
  <li> Misc. notes
    <ul>
      <li>We use different vectorizers for each region of the document - title, summary, and content, and later use a weighted combination as explained above.</li>
      <li>We considered using separate vectorizers for bigrams and then using a weighted combination of unigram and bigram vectors, but this would help much because bigrams would only help in reordering the query, and if a candidate query expansion is a bigram, the tf-idf scores for both terms in the bigram would be similar, and would already be considered in the correct order in our current approach.</li>
      <li>We do not use stemming as it gives no observable benefits (as expected).</li>
      <li>We note that we could possibly handle query drifts (leading to lower precisions in subsequent rounds) if we were allowed to drop words from the query (we cannot drop a word once it becomes a part of the query), by restarting the process with new candidates for expansion from the iteration where the precision was higher.</li>
      <li>Intuitively, we are increasing the scores of words which occur only in relevant documents (more weight to summaries), and penalizing words which occur only in non-relevant documents, and readjusting and considering words which occur in both sets.</li>
      <li>We thought about implementing a probabilistic approach or an approach based on ML, but both we thought both would perform worse in the given experiment setting, and with given resources.</li>
      <li>We use 1+log(tf), and log(N/df) for tf-idf scoring.</li>
      <li>We preprocess the data in background threads (which are efficient for I/O jobs).</li>
    </ul>
  </li>
</ol>
