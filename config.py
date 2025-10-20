import os

BASE_PATH = os.path.dirname(__file__)
RAW_DATA_PATH =os.path.join(BASE_PATH, './data/douban_top250_movies.json')
ENTITIES_PATH =os.path.join(BASE_PATH, './data/entities.txt')

NEO4J_URI='neo4j+s://ce7d909d.databases.neo4j.io'
NEO4J_USERNAME='neo4j'
NEO4J_PASSWORD='xJ9wCJYoBYyfZAldtl60l1RzQyVnXHm73qfmIRKjDMw'


SYNONYMS_MAP = {
    'attributes': {
        '评分': '评分',
        '打分': '评分',
        '分数': '评分',
        '简介': '简介',
        '介绍': '简介',
        '类型': '类型',
        '类别': '类型',
        '国家': '国家',
        '哪里': '国家',
        '语言': '语言',
        '上映': '上映',
        '发布': '上映',
        '片长': '片长',
        '时长': '片长',
    },
    'relations': {
        '主演': '主演',
        '演员': '主演',
        '演的': '主演',
        '演过': '主演',
        '导演': '导演',
        '执导': '导演',
        '编剧': '编剧',
    }
}