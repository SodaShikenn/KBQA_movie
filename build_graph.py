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
            # 导演
            for director in movie['directors']:
                print(movie['directors'])

                director_name = director[1]
                dct = {'name': director_name}
                if dct not in self.entity_data['PERSON']:
                    self.entity_data['PERSON'].append(dct)
                self.relation_data['导演'].append((movie_name, director_name))
            # 编剧
            for writer in movie['writers']:
                writer_name = writer[1]
                dct = {'name': writer_name}
                if dct not in self.entity_data['PERSON']:
                    self.entity_data['PERSON'].append(dct)
                self.relation_data['编剧'].append((movie_name, writer_name))
            # 主演
            for actor in movie['actors']:
                actor_name = actor[1]
                dct = {'name': actor_name}
                if dct not in self.entity_data['PERSON']:
                    self.entity_data['PERSON'].append(dct)
                self.relation_data['主演'].append((movie_name, actor_name))
    # 缓存实体文件
    def dump_entitys(self):
        entitys = []
        for label, entity_list in self.entity_data.items():
            entitys += [entity['name'] for entity in entity_list]
        with open(ENTITYS_PATH, 'w', encoding='utf-8') as file:
            file.write('\n'.join(entitys))

if __name__ == '__main__':
    bg = BuildGraph()
    bg.dump_entitys()
