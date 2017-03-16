import urllib2
import json
from newspaper import Article
from bs4 import BeautifulSoup


class GoogleNewsScraper:
    def __init__(self):
        self.user_agent = "Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"

    def query(self, search_terms):
        self.web_request = urllib2.Request('http://www.google.com/search?q={query}'.format(query=search_terms))
        self.news_request = urllib2.Request('http://www.google.com/search?q={query}&tbm=nws'.format(query=search_terms))
        self.web_request.add_header('User-Agent', self.user_agent)
        self.news_request.add_header('User-Agent', self.user_agent)
        self.article_objects_parsed = []

    def fetch_news_results(self):
        news_response = urllib2.urlopen(self.news_request)
        news_response_html = news_response.read()
        soup = BeautifulSoup(news_response_html, 'html.parser')
        news_soup_body = soup.body
        news_search_links = [search_result.a.get("href").strip('/url?q=')
                             for search_result in news_soup_body.find_all("h3")]
        cleaned = {'news-'+str(index): link[:link.index('&sa')] for index, link in enumerate(news_search_links)}
        return cleaned

    def fetch_json_result(self):
        return json.dumps({"news": self.fetch_news_results()})

    def parse_news_articles(self):
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
        self.dow30url = "http://money.cnn.com/data/dow30/"
        self.user_agent = "Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"
        self.dow_request = urllib2.Request(self.dow30url)
        self.dow_request.add_header('User-Agent',
                                    self.user_agent)
        self.dow30prices = []

    def scrape_prices(self):
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


if __name__ == '__main__':
    googleNews = GoogleNewsScraper()
    googleNews.query('3M')
    res = googleNews.fetch_news_results()

    dowToday = Dow30Scraper()
    dowToday.scrape_prices()