import urllib.request
import urllib.parse
import json
import threading
import datetime
import feedparser
import matplotlib
import datetime
from multiprocessing import Pool
from urllib.request import urlopen
from google import search
from newspaper import Article
from bs4 import BeautifulSoup
from cik import maps
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from string import punctuation
import time

#matplotlib.rcParams.update({'font.size': 8})


class GoogleNewsScraper:
    def __init__(self):
        """
        Scrape google news' first page results for a queried company
        """
        self.kwargs = {'tpe': 'nws',
                       'stop': 15,
                       'tbs': 'cdr:1,cd_min:3/24/2017,cd_max:3/23/2017'}
        self.article_objects_parsed = []

    def fetch_news_results(self, company_name):
        """
        This method returns the first page search result urls in a dictionary representation
        for newspaper module to parse them.
        :return:
        """
        try:
            news_search_links = list(search(company_name, **self.kwargs))
            result_links = [link for link in news_search_links]
            print('GoogleNews scraped!')
        except:
            result_links = []

        return result_links

    def fetch_json_result(self, company_name):
        """
        Returns json representation of the results.
        :return:
        """
        return json.dumps({"news": self.fetch_news_results(company_name)})

    def parse_news_articles(self, company_name):
        """
        Returns newspaper's Article instances of the scraped first page news results
        :return:
        """
        news_urls_dict = self.fetch_news_results(company_name)
        for id in news_urls_dict:
            url = news_urls_dict[id]
            article = Article(url)
            article.download()
            article.parse()
            self.article_objects_parsed.append(article)

        return self.article_objects_parsed


class YahooFinanceNewsScraper:
    def __init__(self):
        self.finance_url = 'http://finance.yahoo.com/rss/headline?s={company_name}'
        self.article_objects_parsed = []

    def fetch_news_results(self, company_name):
        """
        This method returns the first page search result urls in a dictionary representation
        for newspaper module to parse them.
        :return:
        """
        self.article_objects_parsed = []
        try:
            feed = feedparser.parse('http://finance.yahoo.com/rss/headline?'+
                                    urllib.parse.urlencode({'s':company_name}))

            result_links = [search_result.link
                                 for search_result in feed['entries']]
            print('Yahoo News scraped!')
        except:
            result_links = []
        return result_links

    def parse_news_articles(self, company_name):
        """
        Returns newspaper's Article instances of the scraped first page news results
        :return:
        """
        self.article_objects_parsed = []
        news_urls_dict = self.fetch_news_results(company_name)
        print(company_name)
        for id in news_urls_dict:
            try:
                url = news_urls_dict[id]
                article = Article(url)
                article.download()
                article.parse()
                self.article_objects_parsed.append(article)
            except Exception as e:
                continue
        return self.article_objects_parsed


class Dow30Scraper:
    def __init__(self):
        """
        This class is used to scrape the DOW 30 prices at the instant of running.
        """
        self.dow30url = "http://money.cnn.com/data/dow30/"
        self.user_agent = "Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"
        self.dow_request = urllib.request.Request(self.dow30url)
        self.dow_request.add_header('User-Agent',
                                    self.user_agent)
        self.dow30prices = []

    def scrape_prices(self):
        """
        Returns a dictionary representation of DOW 30 company stock prices and their change
        For top 5 best and worst performers in ascending order
        {
          "company_name": "name",
          "symbol" : "NN",
          "current_price": 323,
          "change" : +0.1
        }
        :return:
        """
        dow_response_html = urlopen(self.dow_request).read()
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
            price_change_percentage = float(price_cols[2].find("span").text.strip('%'))
            self.dow30prices.append({"company_name": name,
                                     "symbol": symbol,
                                     "current_price": current_price,
                                     "change": change_in_price,
                                     "change_percentage": price_change_percentage})

        # Sort the companies according to change %
        self.dow30prices = sorted(self.dow30prices, key=lambda data: data['change_percentage'])
        return self.dow30prices[:2] + self.dow30prices[-2:]


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
        self.dow_request = urllib.request.Request(self.k8url)
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

        rss_request_url = self.k8url + '?' + urllib.parse.urlencode(self.params)
        feed = feedparser.parse(rss_request_url)
        for entry in feed['entries']:
            filing_date = datetime.datetime.strptime(entry['filing-date'], "%Y-%m-%d").date()
            date_limit = datetime.datetime.now().date()-datetime.timedelta(days=4)
            # Check if 8-K report has been filed in last 2 days
            if filing_date > date_limit:
                self.k8_urls.append(self.scrape_k8_url(entry['filing-href']))

    @staticmethod
    def scrape_k8_url(self, url):
        """
        Helper method to scrape the url of 8-K filing
        :param url:
        :return:
        """
        response_html = urlopen(url).read()
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
            try:
                article = Article(k8_url)
                while not article.is_downloaded:
                    article.download()
                article.parse()
                self.k8_filings_parsed.append(article)
            except Exception as e:
                print(e.message)
                continue
        return self.k8_filings_parsed


class ArticleAnalyser:
    def __init__(self):
        self._stopwords = set(list(punctuation))
        with open('finance.json') as datafile:
            self._senti_lexicon = json.load(datafile)

    def analyse(self, article):
        """
        Returns the overall sentiment based on the socialsent's Financial lexicon
        Takes article dict as the argument
        :param article:
        :return:
        """
        positive_sentiment_dataframe = {} # Positive score: Number of sentences with that score
        negative_sentiment_dataframe = {} # Negative score: Number of sentences with that score
        neutral_sentiment_dataframe = {0:0} # 0: Number of sentences with that score
        total_positive_indicator = 0
        total_negative_indicator = 0
        total_neutral_indicator = 0
        sentences = [sentence for sentence in sent_tokenize(article['text'])]
        for sentence in sentences:
            sentence_words = [word.strip(punctuation).lower() for word in word_tokenize(sentence)]
            sentence_sentiment_score = 0
            for word in sentence_words:
                sentence_sentiment_score += self._senti_lexicon[word] if word in self._senti_lexicon else 0
            if sentence_sentiment_score > 0:
                if sentence_sentiment_score in positive_sentiment_dataframe:
                    positive_sentiment_dataframe[sentence_sentiment_score] += 1
                else:
                    positive_sentiment_dataframe[sentence_sentiment_score] = 1
            elif sentence_sentiment_score < 0:
                if sentence_sentiment_score in negative_sentiment_dataframe:
                    negative_sentiment_dataframe[sentence_sentiment_score] += 1
                else:
                    negative_sentiment_dataframe[sentence_sentiment_score] = 1
            else:
                neutral_sentiment_dataframe[0] += 1

        for pos_score in positive_sentiment_dataframe:
            total_positive_indicator += pos_score*positive_sentiment_dataframe[pos_score]
        for neg_score in negative_sentiment_dataframe:
            total_negative_indicator += abs(neg_score*negative_sentiment_dataframe[neg_score])
        total_neutral_indicator = neutral_sentiment_dataframe[0]

        total_score = total_positive_indicator + abs(total_negative_indicator) + total_neutral_indicator
        try:
            degree_of_positivity = (total_positive_indicator/total_score)*100
            degree_of_negativity = (total_negative_indicator/total_score)*100
            degree_of_neutrality = (total_neutral_indicator/total_score)*100
        except ZeroDivisionError:
            pass

        return [article, degree_of_positivity, abs(degree_of_negativity), degree_of_neutrality]

    def article_date_valid(self, article):
        return article.publish_date.day <= 24 and article.publish_date.day >=23 if article.publish_date is not None else True # article.publish_date.month ==3

    def download_and_parse(self, article_url):
        try:
            article = Article(article_url)
            retry_limits = 20
            retry_count = 0
            while not article.is_downloaded and retry_count<retry_limits:
                article.download()
                retry_count += 1
                print('Retrying for {} time(s)'.format(retry_count))
            article.parse()
            if 'finance.yahoo.com' in article_url:
                publish_time_tag = BeautifulSoup(article.html,'html.parser').find_all(itemprop="datePublished")[0].get('content')
                article.publish_date = datetime.datetime.strptime(publish_time_tag, '%Y-%m-%dT%H:%M:%SZ')
            if self.article_date_valid(article):
                print(article.publish_date, 'date')
                print(article.title, 'downloaded')
                print(article_url)
                return {'text': article.text,
                        'title': article.title,
                        'url': article.url}
            else:
                pass
        except Exception as e:
            print(article_url)
            print("download error: {}".format(e))
            pass