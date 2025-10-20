import json
from config import *

class BuildGraph():
    def __init__(self):
        # 解析json数据
        self.parse_raw_data()

    def parse_raw_data(self):
        with open(RAW_DATA_PATH, encoding='utf-8') as file:
            lines = file.readlines()
        # 逐行解析
        for line in lines:
            movie = json.loads(line)
            movie_name = movie['name']
            print(movie_name)
            exit()

if __name__ == '__main__':
    bg = BuildGraph()