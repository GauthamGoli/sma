import time
import matplotlib.pyplot as plt
from multiprocessing import Pool
from operator import add
from nltk import sent_tokenize, word_tokenize
from scraper import ArticleAnalyser, YahooFinanceNewsScraper, GoogleNewsScraper, Dow30Scraper, K8Scraper


def write_output(stock, text):
    f = open(stock, 'w')
    f.write(text)
    f.close()

# Scrape current DOW 30 prices
start_time = time.time()
dowToday = Dow30Scraper()
companies = dowToday.scrape_prices()
article_urls = []
# Scrape and parse news related to company
yahooNews = YahooFinanceNewsScraper()
googleNews = GoogleNewsScraper()
analyser = ArticleAnalyser()
plt.figure(1)
for company_index, company in enumerate(companies):
    start_time_cp = time.time()

    article_urls = googleNews.fetch_news_results(company['company_name'])
   # article_urls = yahooNews.fetch_news_results(company['symbol'])
    
    print(article_urls)
    end_time_dl = time.time()
    print('Time to fetch RSS feed for {} : {}'.format(company['symbol'],
                                                      start_time_cp - end_time_dl))  # Debug statement, Remove before final submission
    with Pool(5) as p:
        article_list = p.map(analyser.download_and_parse, article_urls)

    article_titles = []
    for article in article_list:
        article_objects_parsed = [article for article in article_list if article is not None and article['text']]

    end_time_cp = time.time()
    print('time to fetch for a company: {}'.format(
        end_time_cp - start_time_cp))  # Debug statement, Remove before final submission
    print(company['company_name'], ': Change % :', company['change_percentage'])
    x = []
    y_positivity = []
    y_negativity = []
    y_neutrality = []
    y_overall = []
    colors = []
    for article_index, article_obj in enumerate(article_objects_parsed):
        article, positivity_score, negativity_score, neutrality_score = analyser.analyse(article_obj)
        article_obj['positivity_score'] = positivity_score
        article_obj['negativity_score'] = negativity_score
        article_obj['neutrality_score'] = neutrality_score
        x.append(article_index)
        y_positivity.append(positivity_score)
        y_negativity.append(negativity_score)
        y_neutrality.append(neutrality_score)
        y_overall.append([positivity_score, negativity_score, neutrality_score, article])

    plt.subplot(2, 2, company_index + 1)
    plt.tight_layout()
    if company_index == 4:
        plt.ylabel("senti_score")
    if company_index == 8:
        plt.xlabel("article_index")
    if company['change_percentage'] < 0:
        y_overall = list(sorted(y_overall, key=lambda y: y[2]))
        y_overall = list(reversed(sorted(y_overall, key = lambda y: y[1])))
        y_positivity = [y[0] for y in y_overall]
        y_negativity = [y[1] for y in y_overall]
        y_neutrality = [y[2] for y in y_overall]
        plt.bar(x, y_negativity, color = 'red')
        plt.bar(x, y_positivity, bottom = y_negativity, color = 'blue')
        plt.bar(x, y_neutrality, bottom = list(map(add, y_negativity, y_positivity)), color='black')
    else:
        y_overall = list(sorted(y_overall, key=lambda y: y[2]))
        y_overall = list(reversed(sorted(y_overall, key = lambda y: y[0])))
        y_positivity = [y[0] for y in y_overall]
        y_negativity = [y[1] for y in y_overall]
        y_neutrality = [y[2] for y in y_overall]
        plt.bar(x, y_positivity, color='blue')
        plt.bar(x, y_negativity, bottom = y_positivity, color='red')
        plt.bar(x, y_neutrality, bottom = list(map(add, y_negativity, y_positivity)), color='black')
    plt.title('{company}: {change}'.format(company=company['company_name'], change=company['change_percentage']))
    write_output('{}.txt'.format(company['symbol']), '\n'.join(
        ['{url} , {title}'.format(url= artcl['url'], title=artcl['title']) for yp, yn, ynn, artcl in y_overall]))

plt.show()

end_time = time.time()
print('Total time: {time} seconds'.format(time=end_time - start_time))

# k8scraper = K8Scraper()
# # Fetch recent k8 filings for a Company
# k8scraper.fetch_recent_k8_filings('UNH')
# article_objects_k8_axp = k8scraper.parse_k8_filings()
