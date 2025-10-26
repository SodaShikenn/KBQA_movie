import os

BASE_PATH = os.path.dirname(__file__)
RAW_DATA_PATH =os.path.join(BASE_PATH, './data/douban_top250_movies.json')
ENTITIES_PATH =os.path.join(BASE_PATH, './data/entities.txt')

NEO4J_URI='neo4j+s://ce7d909d.databases.neo4j.io'
NEO4J_USERNAME='neo4j'
NEO4J_PASSWORD='xJ9wCJYoBYyfZAldtl60l1RzQyVnXHm73qfmIRKjDMw'

THRESHOLD = 0.1

SYNONYMS_MAP = {
    'attributes': {
        # 评分
        '评分': '评分',
        '打分': '评分',
        '分数': '评分',
        '多少分': '评分',
        '几分': '评分',
        '得分': '评分',
        '分值': '评分',
        '评价': '评分',

        # 简介
        '简介': '简介',
        '介绍': '简介',
        '内容': '简介',
        '剧情': '简介',
        '大纲': '简介',
        '故事': '简介',
        '讲什么': '简介',
        '说的什么': '简介',

        # 类型
        '类型': '类型',
        '类别': '类型',
        '题材': '类型',
        '风格': '类型',
        '是什么类型': '类型',
        '什么题材': '类型',

        # 国家 / 地区
        '国家': '国家',
        '哪里': '国家',
        '哪国': '国家',
        '地区': '国家',
        '产地': '国家',
        '出品国': '国家',
        '出自哪里': '国家',

        # 语言
        '语言': '语言',
        '配音': '语言',
        '说的是什么语言': '语言',

        # 上映时间
        '上映': '上映',
        '发布': '上映',
        '上映时间': '上映',
        '什么时候上映': '上映',
        '首映': '上映',
        '什么时候出的': '上映',
        '出了什么时候': '上映',
        '上映日期': '上映',

        # 片长 / 时长
        '片长': '片长',
        '时长': '片长',
        '多长': '片长',
        '放多久': '片长',
        '播放时间': '片长',
        '片子多长': '片长',
    },

    'relations': {
        # 主演
        '主演': '主演',
        '演员': '主演',
        '演的': '主演',
        '演过': '主演',
        '谁演的': '主演',
        '出演': '主演',
        '参演': '主演',
        '饰演': '主演',
        '扮演': '主演',

        # 导演
        '导演': '导演',
        '执导': '导演',
        '拍的': '导演',
        '谁拍的': '导演',
        '导的': '导演',
        '拍摄': '导演',

        # 编剧
        '编剧': '编剧',
        '写的': '编剧',
        '谁写的': '编剧',
        '剧本': '编剧',
        '撰写': '编剧',
        '创作': '编剧',
    }
}

TEMPLATES = [
    {
        'question': '%ENT%的%REL%是谁/有哪些',
        'cypher': "MATCH (n {name:'%ENT%'})-[:%REL%]->(m) RETURN SUBSTRING(REDUCE(s = '', x IN COLLECT(m.name) | s + ' / ' + x), 3) AS RES",
        'answer': '%ENT%的%REL%：RES',
        'slots': '{"%ENT%": 1, "%REL%": 1}',
        'example': '霸王别姬的导演是谁？大话西游的主演有哪些？',
    },
    {
        'question': '%ENT%%REL%过哪些电影',
        'cypher': "MATCH (n)-[:%REL%]->(m {name:'%ENT%'}) RETURN SUBSTRING(REDUCE(s = '', x IN COLLECT(n.name) | s + ' / ' + x), 3) AS RES",
        'answer': '%ENT%%REL%过的电影：RES',
        'slots': '{"%ENT%":1, "%REL%":1}',
        'example': '张国荣主演过哪些电影？周星驰导演过哪些电影？',
    },
    {
        'question': '%ENT0%和%ENT1%是什么关系',
        'cypher': "MATCH (n {name:'%ENT0%'})-[rel]->(m {name:'%ENT1%'}) RETURN SUBSTRING(REDUCE(s = '', x IN COLLECT(type(rel)) | s + ' / ' + x), 3) AS RES",
        'answer': '%ENT1%是%ENT0%的：RES',
        'slots': '{"%ENT%":2}',
        'example': '张国荣和霸王别姬是什么关系？',
    },
    {
        'question': '%ENT%的%ATT%',
        'cypher': "MATCH (n {name:'%ENT%'}) return n.%ATT% AS RES",
        'answer': '%ENT%的%ATT%是：RES',
        'slots': '{"%ENT%":1, "%ATT%":1}',
        'example': '霸王别姬的片长？阿甘正传的豆瓣评分是多少？',
    }
]