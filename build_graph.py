import json
from collections import defaultdict
from config import *

class BuildGraph():
    def __init__(self):
        self.entity_data = defaultdict(list)
        self.relation_data = defaultdict(list)
        # 解析json数据
        self.parse_raw_data()

    def parse_raw_data(self):
        with open(RAW_DATA_PATH, encoding='utf-8') as file:
            lines = file.readlines()
        # 逐行解析
        for line in lines:
            movie = json.loads(line)
            movie_name = movie['name']
            # 组装电影实体数据
            self.entity_data['MOVIE'].append({
                'id': movie['id'],
                'name': movie_name,
                '评分': movie['rating_num'],
                '介绍': movie['summary'],
                '类型': '/'.join(movie['genres']),
                '国家': '/'.join(movie['countries']),
                '语言': '/'.join(movie['languages']),
                '上映': '/'.join(movie['pubdates']),
                '片长': '/'.join(movie['durations']),
            })
            print(self.entity_data)
            exit()

            
if __name__ == '__main__':
    bg = BuildGraph()