import requests
from bs4 import BeautifulSoup
import re, json
from tqdm import tqdm
import traceback

class Crawler():
    pass

if __name__ == '__main__':
    crawler = Crawler()
    for i in range(10):
        url = 'https://movie.douban.com/top250?start=%s&filter=' % str(i*25)
        print(url)
