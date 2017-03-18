import urllib
import urllib2
import json
import datetime
import feedparser
from newspaper import Article
from bs4 import BeautifulSoup
from cik import maps
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from string import punctuation


class GoogleNewsScraper:
    def __init__(self):
        """
        Scrape google news' first page results for a queried company
        """
        self.user_agent = "Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"

    def query(self, company_name):
        """
        This method constructs the request objects for a particular query
        :param search_terms:
        :return:
        """
        self.web_request = urllib2.Request('http://www.google.com/search?q={query}'.format(query=company_name))
        self.news_request = urllib2.Request('http://www.google.com/search?q={query}&tbm=nws'.format(query=company_name))
        self.web_request.add_header('User-Agent', self.user_agent)
        self.news_request.add_header('User-Agent', self.user_agent)
        self.article_objects_parsed = []

    def fetch_news_results(self):
        """
        This method returns the first page search result urls in a dictionary representation
        for newspaper module to parse them.
        :return:
        """
        news_response = urllib2.urlopen(self.news_request)
        news_response_html = news_response.read()
        soup = BeautifulSoup(news_response_html, 'html.parser')
        news_soup_body = soup.body
        news_search_links = [search_result.a.get("href").strip('/url?q=')
                             for search_result in news_soup_body.find_all("h3")]
        cleaned = {'news-'+str(index): link[:link.index('&sa')] for index, link in enumerate(news_search_links)}
        return cleaned

    def fetch_json_result(self):
        """
        Returns json representation of the results.
        :return:
        """
        return json.dumps({"news": self.fetch_news_results()})

    def parse_news_articles(self):
        """
        Returns newspaper's Article instances of the scraped first page news results
        :return:
        """
        news_urls_dict = self.fetch_news_results()
        for id in news_urls_dict:
            url = news_urls_dict[id]
            article = Article(url)
            article.download()
            article.parse()
            self.article_objects_parsed.append(article)

        return self.article_objects_parsed


class Dow30Scraper:
    def __init__(self):
        """
        This class is used to scrape the DOW 30 prices at the instant of running.
        """
        self.dow30url = "http://money.cnn.com/data/dow30/"
        self.user_agent = "Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"
        self.dow_request = urllib2.Request(self.dow30url)
        self.dow_request.add_header('User-Agent',
                                    self.user_agent)
        self.dow30prices = []

    def scrape_prices(self):
        """
        Returns a dictionary representation of DOW 30 company stock prices and their change
        {
          "company_name": "name",
          "symbol" : "NN",
          "current_price": 323,
          "change" : +0.1
        }
        :return:
        """
        dow_response_html = urllib2.urlopen(self.dow_request).read()
        soup = BeautifulSoup(dow_response_html, 'html.parser')
        dow_soup_body = soup.body
        dow_table = dow_soup_body.find("table", "wsod_dataTable")
        dow_rows = dow_table.find_all("tr")[1:]
        for row in dow_rows:
            symbol = row.find("a", "wsod_symbol").text
            name = row.find("a", "wsod_symbol").find_next_sibling("span").text
            price_cols = row.find_all("span", "wsod_stream")
            current_price = float(price_cols[0].text)
            change_in_price = float(price_cols[1].find("span").text)
            self.dow30prices.append({"company_name": name,
                                     "symbol": symbol,
                                     "current_price": current_price,
                                     "change": change_in_price})
        return self.dow30prices


class K8Scraper:
    def __init__(self):
        """
        This class can be used to fetch the recent 8-K filings of a company in the last
        3 days by querying the EDGAR Search engine.

        Its named K8 everywhere as variables can't start with a number :)
        """
        self.k8url = 'https://www.sec.gov/cgi-bin/browse-edgar'
        self.params = {'action': 'getcompany',
                       'CIK': '',
                       'type': '8-k',
                       'dateb': 'b',
                       'owner': 'include',
                       'start': 0,
                       'count': 30,
                       'output': 'atom'}
        self.user_agent = "Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"
        self.dow_request = urllib2.Request(self.k8url)
        self.dow_request.add_header('User-Agent',
                                    self.user_agent)
        self.k8_filings_parsed = []
        self.k8_urls = []

    def fetch_recent_k8_filings(self, company_symbol):
        """
        This method has to be called with the company symbol as the argument to fetch the url's corresponding
        to 8-K filings of that company. We just need the urls for newspaper module to process them.
        :param company_symbol:
        :return:
        """
        self.k8_urls = []
        cik_number = maps[company_symbol]
        self.params['CIK'] = cik_number

        rss_request_url = self.k8url + '?' + urllib.urlencode(self.params)
        feed = feedparser.parse(rss_request_url)
        for entry in feed['entries']:
            filing_date = datetime.datetime.strptime(entry['filing-date'], "%Y-%m-%d").date()
            date_limit = datetime.datetime.now().date()-datetime.timedelta(days=4)
            # Check if 8-K report has been filed in last 2 days
            if filing_date > date_limit:
                self.k8_urls.append(self.scrape_k8_url(entry['filing-href']))

    def scrape_k8_url(self, url):
        """
        Helper method to scrape the url of 8-K filing
        :param url:
        :return:
        """
        response_html = urllib2.urlopen(url).read()
        soup = BeautifulSoup(response_html, 'html.parser')
        k8_filings_body = soup.body
        k8_filing_link = k8_filings_body.find("table", "tableFile").find("a").get("href")
        k8_url = 'https://www.sec.gov' + k8_filing_link
        return k8_url

    def parse_k8_filings(self):
        """
        This method returns the newspaper's Article instances of 8-K filings of queried company
        :return:
        """
        self.k8_filings_parsed = []
        for k8_url in self.k8_urls:
            article = Article(k8_url)
            article.download()
            article.parse()
            self.k8_filings_parsed.append(article)
        return self.k8_filings_parsed


class ArticleAnalyser:
    def __init__(self):
        self._stopwords = set(list(punctuation))
        with open('finance.json') as datafile:
            self._senti_lexicon = json.load(datafile)

    def analyse(self, article):
        """
        Returns the overall sentiment based on the socialsent's Financial lexicon
        Takes newspaper's article object as the argument
        :param article:
        :return:
        """
        words = [word.strip(punctuation) for word in word_tokenize(article.text.lower())]
        senti_score = 0
        for word in words:
            if word in self._senti_lexicon:
                senti_score += self._senti_lexicon[word]

        return [article, senti_score]

if __name__ == '__main__':

    # Examples
    # Scrape current DOW 30 prices
    dowToday = Dow30Scraper()
    dowToday.scrape_prices()

    # Scrape and parse news related to company
    googleNews = GoogleNewsScraper()
    googleNews.query('3M')
    article_objects_news = googleNews.parse_news_articles()


    k8scraper = K8Scraper()
    # Fetch recent k8 filings for a Company
    k8scraper.fetch_recent_k8_filings('MMM')
    article_objects_k8_axp = k8scraper.parse_k8_filings()

    analyser = ArticleAnalyser()

    for article_obj in article_objects_news:
        print analyser.analyse(article_obj)