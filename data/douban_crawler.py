import requests
from bs4 import BeautifulSoup
import re, json
from tqdm import tqdm
import traceback



class Crawler(): #豆瓣有个简单的反爬策略，他会判断是不是通过浏览器访问，所以要加一个UA头，伪装成一个浏览器的访问
    def __init__(self):
        self.headers = {
            'User-Agent' :'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0'  
            }
    
    def get_movie_list(self, url):
        response = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'html.parser') # bs4解析电影节点
        node_a = soup.select('#content .grid_view .item .hd a')
        detail_list = []
        for a in node_a:
            name = a.select('span')[0].text # 只要中文名
            url = a.attrs['href'] # 获取片名列表
            detail_list.append([name, url])
        return detail_list

if __name__ == '__main__':
    crawler = Crawler()
    for i in range(10):
        url = 'https://movie.douban.com/top250?start=%s&filter=' % str(i*25)
        movie_list = crawler.get_movie_list(url)
        print(movie_list)
