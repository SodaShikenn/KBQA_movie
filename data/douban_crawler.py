import requests
from bs4 import BeautifulSoup
import re, json
from tqdm import tqdm
import traceback

class Crawler(): 

    # 豆瓣有个简单的反爬策略,他会判断是不是通过浏览器访问,所以要加一个UA头,伪装成一个浏览器的访问
    def __init__(self):
        self.headers = {
            'User-Agent' :'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0'  
            }

    # 获取页面内容
    def get_movie_list(self, url):
        response = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'html.parser') # bs4解析电影节点
        node_a = soup.select('#content .grid_view .item .hd a')
        movie_list = []
        for a in node_a:
            name = a.select('span')[0].text # 只要中文名
            url = a.attrs['href'] # 获取片名列表
            movie_list.append([name, url])
        return movie_list
    
    # 解析movie_id
    def _parse_id(self, url):
        obj = re.search('subject/(.*?)/', url)
        return obj.group(1)    
    
    def _parse_summary(self, info): # 定义电影简介爬取方法
        """
        1)有豆瓣标识符和展开全部:https://movie.douban.com/subject/1292052/

        2)有豆瓣标识符,没有展开全部:https://movie.douban.com/subject/1292722/

        3)只有介绍文本,没有标识符和展开全部:https://movie.douban.com/subject/30170448/
        """
        span = info.select('#link-report-intra span')
        if len(span) >= 2:
            summary = span[-2]
        else:
            summary = span[0]
        return re.sub('\s{2,}', '', summary.text)

    def _parse_directors(self, info): # 定义导演爬取方法
        obj = re.search('<span class="pl">导演</span>: <span class="attrs">(.*?)</span>', info, re.S)
        result = []
        if obj:
            obj_soup = BeautifulSoup(obj.group(1), 'html.parser')
            for a in obj_soup.select('a'):
                result.append((a.attrs['href'], a.text))
        return result

    def _parse_writers(self, info): # 定义编剧爬取方法
        obj = re.search('<span class="pl">编剧</span>: <span class="attrs">(.*?)</span>', info, re.S)
        result = []
        if obj:
            obj_soup = BeautifulSoup(obj.group(1), 'html.parser')
            for a in obj_soup.select('a'):
                result.append((a.attrs['href'], a.text))
        return result
    
    def _parse_actors(self, info): # 定义主演爬取方法
        obj = re.search('<span class="pl">主演</span>: <span class="attrs">(.*?)</span>', info, re.S)
        result = []
        if obj:
            obj_soup = BeautifulSoup(obj.group(1), 'html.parser')
            for a in obj_soup.select('a'):
                result.append((a.attrs['href'], a.text))
        return result
    
    def _parse_genres(self, info): # 定义影片类型爬取方法
        obj = re.search('<span class="pl">类型:(.*?)<br/>', info, re.S)
        result = []
        if obj:
            obj_soup = BeautifulSoup(obj.group(1), 'html.parser')
            for span in obj_soup.select('span'):
                result.append(span.text)
        return result

    def _parse_countries(self, info): # 定义制片国家/地区爬取方法
        obj = re.search('<span class="pl">制片国家/地区:</span>(.*?)<br/>', info, re.S)
        result = []
        if obj:
            result = [t.strip() for t in obj.group(1).split('/')]
        return result

    def _parse_languages(self, info): # 定义发行语言爬取方法
        obj = re.search('<span class="pl">语言:</span>(.*?)<br/>', info, re.S)
        result = []
        if obj:
            result = [t.strip() for t in obj.group(1).split('/')]
        return result

    def _parse_pubdates(self, info): # 定义上映日期爬取方法
        obj = re.search('<span class="pl">上映日期:</span>(.*?)<br/>', info, re.S)
        result = []
        if obj:
            obj_soup = BeautifulSoup(obj.group(1), 'html.parser')
            for span in obj_soup.select('span'):
                result.append(span.text)
        return result
    
    def _parse_durations(self, info): # 定义片长爬取方法
        obj = re.search('<span class="pl">片长:</span>(.*?)<br/>', info, re.S)
        result = []
        if obj:
            obj_soup = BeautifulSoup(obj.group(1), 'html.parser')
            for t in obj_soup.text.split('/'):
                result.append(t.strip())
        return result
    
    def _parse_other_names(self, info): # 定义影片别名爬取方法
        obj = re.search('<span class="pl">又名:</span>(.*?)<br/>', info, re.S)
        result = []
        if obj:
            for t in obj.group(1).split('/'):
                result.append(t.strip())
        return result

    def _parse_imdb(self, info): # 定义IMDb编号爬取方法
        obj = re.search('<span class="pl">IMDb:</span>(.*?)<br/>', info, re.S)
        return obj.group(1).strip() if obj else ''


    # 定义详情页爬取方法
    def get_movie_detail(self, detail):
        try:
            name, url = detail
            movie = {} # 保存信息
            movie['name'] = name
            movie['url'] = url
            movie['id'] = self._parse_id(url)
            # 获取页面源码
            response = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            # 解析外层节点内容
            movie['img'] = soup.select('#mainpic img')[0].attrs['src'] # 电影封面图
            movie['rating_num'] = soup.select('#interest_sectl .rating_num')[0].text # 豆瓣评分
            movie['summary'] = self._parse_summary(soup) # 电影简介
            # 获取info节点源码
            info = str(soup.select('#info')[0]) # 使用正则匹配解析bs4筛选出的节点时，可能会和html源码格式不完全相同，要以转化后的文本为准。
            # with open('info.html', 'w') as file:
            #     file.write(info)
            movie['directors'] = self._parse_directors(info) # 导演信息
            movie['writers'] = self._parse_writers(info) # 编剧信息
            movie['actors'] = self._parse_actors(info) # 主演信息
            movie['genres'] = self._parse_genres(info) # 影片类型
            movie['countries'] = self._parse_countries(info) # 制片国家/地区
            movie['languages'] = self._parse_languages(info) # 发行语言
            movie['pubdates'] = self._parse_pubdates(info) # 上映日期
            movie['durations'] = self._parse_durations(info) # 片长
            movie['other_names'] = self._parse_other_names(info) # 影片别名
            movie['imdb'] = self._parse_imdb(info) # IMDb编号

            # 写入json文件
            with open('douban_top250_movies.json', 'a') as file:
                file.write(json.dumps(movie, ensure_ascii=False) + '\n')

        # 捕获异常
        except Exception as e: 
            print('Error:', detail, traceback.print_exc())


if __name__ == '__main__':
    crawler = Crawler()
    for i in range(10):
        url = 'https://movie.douban.com/top250?start=%s&filter=' % str(i*25)
        movie_list = crawler.get_movie_list(url)
        for detail in tqdm(movie_list, desc=f'第{i}页'):
            crawler.get_movie_detail(detail)
