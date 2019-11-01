from bs4 import BeautifulSoup
from urllib.request import urlopen, urlretrieve, Request
import re
import time
import pickle
import os


def search(query, page_limit=None):  # scans Google News RSS feed for query
    query = query.replace(' ', '%20')
    news_url = 'https://news.google.com/rss/search?q={}'.format(query)
    # news_url = 'https://news.google.com/news/rss/headlines/section/topic/BUSINESS'
    client = urlopen(news_url)
    xml_page = client.read()
    client.close()
    soup_page = BeautifulSoup(xml_page, 'xml')
    news_list = soup_page.find_all('item')
    return news_list[:page_limit]


def search_results(news_list):
    for news in news_list:
        print(news.title.text)
        print(news.link.text)
        print(news.pubDate.text)
        print(news.source.text)
        print('-' * 60)


def archive(archive_path, news_list):  # crawls each html link and archives it if not in dict (archive_dict.pkl)
    try:
        file = open(archive_path + 'archive_dict.pkl', 'rb')
        archive_dict = pickle.load(file)
        file.close()
    except:
        archive_dict = dict()

    success = 0
    failed = 0
    for news in news_list:
        title = re.sub('[\/:*?"<>|]', '#', news.title.text)  # FIXME: redundant character escape
        struc_time = time.strptime(news.pubDate.text[5:-4], '%d %b %Y %H:%M:%S')
        timestamp = time.strftime('%Y%m%d%H%M%S', struc_time)
        filename = timestamp + ' ' + title + '.html'
        url = news.link.text
        if filename not in archive_dict:
            try:  # try to download
                urlretrieve(url, archive_path + filename)  # download html
                archive_dict.update({filename: [url, 1, news.source.text]})  # log success
                success += 1
                print(news.title.text)
                print(news.link.text)
                print(news.pubDate.text)
                print(news.source.text)
            except Exception as e:
                print('Failed to Download: ' + url)
                print(e)
                print('Retrying with pseudo-browser...')
                try:  # retry download with pseudo-browser
                    user_agent = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1'
                    headers = {'user-agent': user_agent}
                    request = Request(url, headers=headers)
                    with urlopen(request) as client, open(archive_path + filename, 'wb') as file:
                        html_page = client.read()
                        file.write(html_page)
                        archive_dict.update({filename: [url, 1, news.source.text]})  # log success
                    success += 1
                    print()
                    print(news.title.text)
                    print(news.link.text)
                    print(news.pubDate.text)
                    print(news.source.text)
                except Exception as e:
                    archive_dict.update({filename: [url, 0, news.source.text]})  # log fail
                    print(e)
                    failed += 1
                    pass
                pass
            print('-' * 60)

    with open(archive_path + 'archive_dict.pkl',
              'wb') as file:  # .pkl is only updated after entire new_list is downloaded
        pickle.dump(archive_dict, file)

    return success, failed


def crawl(query, archive_path, page_limit=None):  # main
    if not os.path.exists(archive_path):
        os.makedirs(archive_path)
    print('Crawling ' + '"' + query + '"' + ' news...')
    print('-' * 60)
    news_list = search(query, page_limit)
    success, failed = archive(archive_path, news_list)
    print('Downloaded : ' + str(success), end=' | ')
    print('Failed: ' + str(failed))
    print('-' * 60)


if __name__ == '__main__':
    path = os.getcwd() + '/News Archive/'
    query = input("Enter search query:")
    while True:
        crawl(query, path)
        time.sleep(1)
