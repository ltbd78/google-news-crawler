from webcrawler import crawl
from article_extractor import extract

import os
import time

__author__ = "Linsu Han"
__copyright__ = "Graphen, Inc."
__license__ = "Apache License Version 2.0"
__version__ = "v1.2.4"
__maintainer__ = "Linsu Han"
__email__ = "linsuhan@graphen.ai"
__status__ = "Development"

path = os.getcwd() + '/News Archive/'


def worker(query, working, process, loops, page_limit, timeout=1):
    if not os.path.exists(
            path + 'archive_dict.pkl'):  # performs initial crawl to build archive_dict.pkl (required by article_extractor.py)
        crawl(query, path, page_limit)
    while working:
        for i in range(loops):
            crawl(query, path, page_limit)
            time.sleep(timeout)
        if process:
            extract(path)


if __name__ == '__main__':
    print('Webcrawler ' + __version__)
    print(__author__ + ' - ' + __email__)
    print(__license__ + '\n')

    query = input("Enter search query:")
    loops = int(input("# of Crawls before processing: "))
    page_limit = int(input("Page limit (0 for no limit): "))
    timeout = int(input("Refresh timeout (seconds): "))
    if page_limit == 0:
        page_limit = None
    print('\n')

    worker(query, True, True, loops, page_limit, timeout)
