### Stock Market Analysis

 - Financial domain-specific sentiment lexicon is used for extracting the sentiment of news articles.
 - Third-party libraries are mentioned in `requirements.txt`
 - Data visualization component is also included

## Implementation

Dow 30 prices are scraped for the current day.

We are using [Yahoo financial news API](https://developer.yahoo.com/finance/company.html) and [8-K filings](https://www.sec.gov) of the companies
as the news sources.

Financial domain-specific sentiment lexicon is used for extracting the sentiment of the news articles and reporting the relevant news articles explaining the increase or decrease.

Example visualization:

![sentiment-viz](https://github.com/GauthamGoli/sma/raw/master/test_result.png)