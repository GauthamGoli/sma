## Stock Market Analysis
### Team Members:
 - Sopan Khosla ( 4th year CSE)
 - Lohit Vandanapu (4th year Civil)
 - Karan Desai (3rd year EE)
 - Tushar Choudhary (4th year ECE)
 - Gautham Goli (4th year Civil)

Please find attached with this proposal the source code of our implementation. Some files could not be printed due to size limitations.
The link to complete souce code is https://github.com/gauthamgoli/sma

### Introduction
 - We made this program to scrape the prices of the stocks, and news articles from the internet, and then identify those news articles which best explain the change in price of the stocks.
 - Financial domain-specific sentiment lexicon is used for extracting the sentiment of news articles.
 - Third-party libraries are mentioned in `requirements.txt`
 - Data visualization component is also included

### Financial lexicon creation
 - A state-of-the-art sentiment induction algorithm was combined with well know method of label propagation with high quality word embeddings.
 - A small set of seed words were used to induce accurate domain-specific(in this case **financial** domain) sentiment lexicon achieveing performance comparable with approaches that rely on hand curated resources.
 - To do the Natural Language Processing (NLP) we used the open source `SocialSent` (https://nlp.stanford.edu/projects/socialsent/) package, and the lexicon was created from 8-K filings of publicly listed US companies.

### Dependencies
 - ```sudo apt-get install python-dev```
 - ```sudo apt-get install libxml2-dev libxslt-dev```
 - ```pip install -r requirements.txt```

## Implementation

#####  What is an '8-K'
An 8-K is a report of unscheduled material events or corporate changes at a company that could be of importance to the shareholders or the Securities and Exchange Commission (SEC).

**Dow 30** prices are scraped for the current day from CNN Money(http://money.cnn.com/data/dow30/)
### News sources
 - We are using [Yahoo financial news API](https://developer.yahoo.com/finance/company.html) RSS endpoint  to get the most recent news articles for Dow 30 companies.
 - We have also used 8-K filings(https://www.sec.gov) of the companies as the news sources.

Financial domain-specific sentiment lexicon is used for extracting the sentiment of the news articles and reporting the relevant news articles explaining the increase or decrease.

### Results
 - The plot below shows the sentiment of the extracted news articles for a few comapnies on a particular day.
 - Title shows % change in the Price of stocks, each coloured bar shows the sentiment of a news article which was published about the particular company within the last 3 days.
 - Blue represents positive sentiment and red represents negative sentiment.
 - We have found this method to return the relevant news articles and their sentiment is able to explain the change in the stock prices within an acceptable limit, but we are trying to improve upon the accuracy using advanced methods like a deep convolutional neural network (CNN) and we are confident of implementing that before the final competition.


![sentiment-viz](https://github.com/GauthamGoli/sma/raw/master/test_result.png)

### References
- William L. Hamilton, Kevin Clark, Jure Leskovec, and Dan Jurafsky. Inducing Domain-Specific Sentiment Lexicons from Unlabeled Corpora. ArXiv preprint (arxiv:1606.02820). 2016.
- Ding, Xiao, et al. "Deep Learning for Event-Driven Stock Prediction." IJCAI. 2015.
