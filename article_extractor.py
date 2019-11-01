import os
import pandas as pd
from glob import glob
from goose3 import Goose
import pickle


def process(archive_path, df_dict):
    html_paths = glob('News Archive/*.html')
    goose = Goose()
    new_processed = 0
    old_processed = 0
    with open(archive_path + 'archive_dict.pkl', 'rb') as file:
        archive_dict = pickle.load(file)
    for html_path in html_paths:
        filename = html_path[13:]
        if filename not in df_dict.get('filenames'):
            with open(html_path, 'rb') as file:
                raw_html = file.read()
                article = goose.extract(raw_html=raw_html)
                timestamp = int(html_path[13:27])
                title = article.title
                meta = article.meta_description
                body = article.cleaned_text
                url = archive_dict.get(filename)[0]
                source = archive_dict.get(filename)[2]
                df_dict.get('filenames').update({filename})
                df_dict.get('df').get('timestamp').append(timestamp)
                df_dict.get('df').get('title').append(title)
                df_dict.get('df').get('meta').append(meta)
                df_dict.get('df').get('body').append(body)
                df_dict.get('df').get('url').append(url)
                df_dict.get('df').get('source').append(source)
                new_processed += 1
                print('Processed: ' + filename)
                print('-' * 60)
        else:
            old_processed += 1
    print('Newly Processed: ' + str(new_processed), end=' | ')
    print('Articles in File: ' + str(old_processed + new_processed))
    print('-' * 60)
    with open(archive_path + 'df_dict.pkl', 'wb') as file:
        pickle.dump(df_dict, file)


def extract(archive_path):  # main
    try:
        file = open(archive_path + 'df_dict.pkl', 'rb')
        df_dict = pickle.load(file)
        file.close()
    except:
        df_dict = {'filenames': set(), 'df': {'timestamp': [], 'title': [], 'meta': [], 'body': [], 'source': [], 'url': []}}
    print('Extracting Articles...')
    print('-' * 60)
    process(archive_path, df_dict)
    articles = pd.DataFrame(df_dict.get('df'))
    articles.to_csv(path_or_buf=os.getcwd() + '/articles.csv', index=False)


if __name__ == '__main__':
    path = os.getcwd() + '/News Archive/'
    extract(path)
