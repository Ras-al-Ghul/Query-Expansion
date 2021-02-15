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
 pip install -r requirements.txt
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
   </ul>
</li>
<li>indexer.py
  <ul>
    <li>Extracts the vocabulary</li>
    <li>Gets list of stop words from stop_words.txt</li>
    <li>Builds tfidf of the summary,title and content using TfidfVectorizer from scikit learn.</li>
  </ul>
</li>
<li>rocchio.py
  <ul>
    <li>Uses the tfidf data and extracts the best words for query expansion</li>
  </ul>
</li>
</ol>

## Algorithm
<p>We use rocchio algorithm along with a few improvisations for the query expansion. Goal is reach the expected precision@10 of search results with minimum number of query expansions. <a href="https://en.wikipedia.org/wiki/Evaluation_measures_(information_retrieval)#Precision_at_K">Precision</a> is measured as the number of relevant documents seen in top 10 search result.</p>
<ol>
  <li>Rocchio algorithm is used to rank and extract the words that can be used for the query expansion to obtain better results. Steps:
  <ul>
    <li>Start with the inital query and expected precision.</li>
    <li>Obtain the content of top 10 search results using google search api and bs4.</li>
    <li>Get user feedback to find the relevant and non relevant documents/search results.</li>
    <li>Extract the feature vectors of the documents</li>
    <li>Now add the feature vectors of the relevant documents to the query feature vector.</li>
    <li>Subtract the feature vectors of the non-relevant documents from the query feature vector.</li>
    <li>Sort and pick the top 2 most relevant words form the above resultant feature vector and add to the query.</li>
    <li>repeat from step 2 with the new query until you reach the desired precision.</li>
  </ul>
  </li>
  <li>We give seperate weightages for the words from Summary, Title and Content of html. As summary provided by the google query would contain the key words, while forming the feature vectors of each document, we give the highest weightage to the words present in the summary, followed by content and title.
  </li>
  <li>We reorder the terms in the query after adding the new terms, using the bigrams generated from the content of the search results. Steps:
    <ul>
      <li>Generate the list of bigrams and their probability from the content of the search results.</li>
      <li>After query expansion, generate all permutations of the orders of terms present in the query.</li>
      <li>For each permutation, genertate the bigrams of the query.</li>
      <li>Pick the permutation with highest bigram probability as the new query.</li>
    </ul>
  </li>
</ol>
