import time
import matplotlib.pyplot as plt
from multiprocessing import Pool
from nltk import sent_tokenize, word_tokenize
from scraper import ArticleAnalyser, YahooFinanceNewsScraper, GoogleNewsScraper, Dow30Scraper, K8Scraper


# Scrape current DOW 30 prices
start_time = time.time()
dowToday = Dow30Scraper()
companies = dowToday.scrape_prices()
# Scrape and parse news related to company
yahooNews = YahooFinanceNewsScraper()
googleNews = GoogleNewsScraper()
analyser = ArticleAnalyser()
plt.figure(1)
for company_index, company in enumerate(companies):
    start_time_cp = time.time()

    article_urls = yahooNews.fetch_news_results(company['symbol'])
    # if len(article_urls) < 25:
    #     article_urls.extend(googleNews.fetch_news_results(company_name=company['company_name'])[:35-len(article_urls)])
    # else:
    #     article_urls = article_urls[:25]

    print(article_urls)
    end_time_dl = time.time()
    print('Time to fetch RSS feed for {} : {}'.format(company['symbol'],
                                                      start_time_cp - end_time_dl))  # Debug statement, Remove before final submission
    with Pool(5) as p:
        article_list = p.map(analyser.download_and_parse, article_urls)

    article_titles = []
    for article in article_list:
        article_objects_parsed = [article for article in article_list if article is not None]

    end_time_cp = time.time()
    print('time to fetch for a company: {}'.format(
        end_time_cp - start_time_cp))  # Debug statement, Remove before final submission
    print(company['company_name'], ': Change % :', company['change_percentage'])
    x = []
    y = []
    colors = []
    for article_index, article_obj in enumerate(article_objects_parsed):
        article, senti_score = analyser.analyse(article_obj)
        article_obj['senti_score'] = senti_score
        x.append(article_index)
        y.append(senti_score)
        if senti_score >= 0:
            colors.append('blue')
        else:
            colors.append('red')

    if company['change_percentage'] >= 0:
        # Price of stock increased, output articles with non negative sentiment
        for article_obj in reversed(sorted(article_objects_parsed, key=lambda article: article['senti_score'])):
            if article_obj['senti_score'] < 0:
                break
            print('{url}: {title}'.format(url=article_obj['url'], title=article_obj['title']))
    if company['change_percentage'] < 0:
        # If price of stock decreased, output articles with non positive sentiment
        for article_obj in sorted(article_objects_parsed, key=lambda article: article['senti_score']):
            if article_obj['senti_score'] > 0:
                break
            print('{url}: {title}'.format(url=article_obj['url'], title=article_obj['title']))

    plt.subplot(2, 2, company_index + 1)
    plt.tight_layout()
    if company_index == 4:
        plt.ylabel("senti_score")
    if company_index == 8:
        plt.xlabel("article_index")
    plt.bar(x, y, color=colors)
    plt.title('{company}: {change}'.format(company=company['company_name'], change=company['change_percentage']))

plt.show()

end_time = time.time()
print('Total time: {time} seconds'.format(time=end_time - start_time))

# k8scraper = K8Scraper()
# # Fetch recent k8 filings for a Company
# k8scraper.fetch_recent_k8_filings('UNH')
# article_objects_k8_axp = k8scraper.parse_k8_filings()