"""
电影知识图谱构建模块
功能：从豆瓣Top250电影JSON数据中提取实体和关系，构建Neo4j知识图谱
"""
import json
from collections import defaultdict
from config import *
from py2neo import Graph

class BuildGraph():
    """知识图谱构建类"""
    def __init__(self):
        """
        初始化方法
        - entity_data: 存储实体数据，格式 {实体标签: [实体字典列表]}
          例如: {'MOVIE': [{name: '肖申克的救赎', 评分: 9.7, ...}], 'PERSON': [{name: '蒂姆·罗宾斯'}]}
        - relation_data: 存储关系数据，格式 {关系类型: [(源实体, 目标实体)]}
          例如: {'导演': [('肖申克的救赎', '弗兰克·德拉邦特')]}
        """
        self.entity_data = defaultdict(list)  # 实体数据字典
        self.relation_data = defaultdict(list)  # 关系数据字典

        # 解析json原始数据，填充entity_data和relation_data
        self.parse_raw_data()

        # 连接Neo4j图数据库
        self.graph = Graph(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    def parse_raw_data(self):
        """
        解析原始JSON数据文件
        从douban_top250_movies.json中提取电影实体和人物实体，以及它们之间的关系
        """
        # 读取JSON文件（每行一个JSON对象）
        with open(RAW_DATA_PATH, encoding='utf-8') as file:
            lines = file.readlines()

        # 逐行解析电影数据
        for line in lines:
            movie = json.loads(line)  # 解析JSON字符串为Python字典
            movie_name = movie['name']  # 获取电影名称

            # === 1. 组装电影实体数据 ===
            # 将电影的各种属性（评分、介绍、类型等）打包成字典
            # 数组类型的属性（如genres、countries）用'/'连接成字符串
            self.entity_data['MOVIE'].append({
                'id': movie['id'],                            # 电影ID
                'name': movie_name,                           # 电影名称
                '评分': movie['rating_num'],                   # 豆瓣评分
                '介绍': movie['summary'],                      # 剧情简介
                '类型': '/'.join(movie['genres']),            # 类型（如：剧情/犯罪）
                '国家': '/'.join(movie['countries']),         # 制片国家
                '语言': '/'.join(movie['languages']),         # 语言
                '上映': '/'.join(movie['pubdates']),          # 上映日期
                '片长': '/'.join(movie['durations']),         # 片长
            })
            # === 2. 提取导演实体和关系 ===
            # directors格式: [[id, name], ...] 例如: [['1054521', '弗兰克·德拉邦特']]
            for director in movie['directors']:
                director_name = director[1]  # 取出导演姓名
                dct = {'name': director_name}
                # 去重：如果该导演还未添加到PERSON实体列表中，则添加
                if dct not in self.entity_data['PERSON']:
                    self.entity_data['PERSON'].append(dct)
                # 添加"导演"关系：(电影名, 导演名)
                self.relation_data['导演'].append((movie_name, director_name))

            # === 3. 提取编剧实体和关系 ===
            for writer in movie['writers']:
                writer_name = writer[1]  # 取出编剧姓名
                dct = {'name': writer_name}
                # 去重：避免同一编剧重复添加
                if dct not in self.entity_data['PERSON']:
                    self.entity_data['PERSON'].append(dct)
                # 添加"编剧"关系：(电影名, 编剧名)
                self.relation_data['编剧'].append((movie_name, writer_name))

            # === 4. 提取主演实体和关系 ===
            for actor in movie['actors']:
                actor_name = actor[1]  # 取出演员姓名
                dct = {'name': actor_name}
                # 去重：避免同一演员重复添加
                if dct not in self.entity_data['PERSON']:
                    self.entity_data['PERSON'].append(dct)
                # 添加"主演"关系：(电影名, 演员名)
                self.relation_data['主演'].append((movie_name, actor_name))
    
    def dump_entities(self):
        """
        导出所有实体名称到文本文件
        用途：后续在问答系统中进行实体识别和匹配时使用
        输出格式：每行一个实体名称
        """
        entities = []
        # 遍历所有实体类型（MOVIE, PERSON）
        for label, entity_list in self.entity_data.items():
            # 提取每个实体的name属性
            entities += [entity['name'] for entity in entity_list]

        # 写入文件，每行一个实体名称
        with open(ENTITIES_PATH, 'w', encoding='utf-8') as file:
            file.write('\n'.join(entities))
        print(f"✓ 已导出 {len(entities)} 个实体到 {ENTITIES_PATH}")

    def create_entities(self):
        """
        在Neo4j中创建实体节点
        生成并执行Cypher语句，批量创建所有MOVIE和PERSON节点

        Cypher示例:
        CREATE (:MOVIE {id:"1292052", name:"肖申克的救赎", 评分:"9.7", ...})
        CREATE (:PERSON {name:"蒂姆·罗宾斯"})
        """
        cypher = ''  # 用于累积所有CREATE语句

        # 遍历每种实体类型（MOVIE, PERSON）
        for label, entity_list in self.entity_data.items():
            # 遍历该类型下的每个实体
            for entity in entity_list:
                # 构建属性字符串，格式: key1:"value1", key2:"value2"
                # replace('"', '\\"') 用于转义属性值中的双引号
                attr_text = ', '.join([k + ':"' + v.replace('"', '\\"') + '"' for k, v in entity.items()])

                # 拼接CREATE语句，格式: CREATE (:标签 {属性})
                cql = 'CREATE (:' + label + ' {' + attr_text + '})'
                cypher += cql + '\n'

        # 批量执行所有CREATE语句
        self.graph.run(cypher)
        print(f"✓ 已创建 {sum(len(v) for v in self.entity_data.values())} 个实体节点")

    def create_relations(self):
        """
        在Neo4j中创建关系边
        为电影和人物节点建立"导演"、"编剧"、"主演"三类关系

        Cypher工作流程:
        1. UNWIND: 将关系列表展开为多行
        2. MATCH: 查找源节点和目标节点
        3. MERGE: 创建关系（如果不存在）

        示例:
        UNWIND [{from:"肖申克的救赎", to:"弗兰克·德拉邦特"}] AS row
        MATCH (n1 {name: row.from})
        MATCH (n2 {name: row.to})
        MERGE (n1)-[:导演]->(n2)
        """
        # 遍历每种关系类型（导演、编剧、主演）
        for label, relation_list in self.relation_data.items():
            # 将关系列表转换为JSON格式的字符串
            # 例如: {from:"电影1", to:"人物1"},{from:"电影2", to:"人物2"}
            text = ','.join(['{from:"' + head + '", to:"' + tail + '"}' for head, tail in relation_list])

            # 构建Cypher语句
            cql = f'''
            UNWIND [{text}] AS row
            MATCH (n1 {{name: row.from}})
            MATCH (n2 {{name: row.to}})
            MERGE (n1)-[:{label}]->(n2)
            '''

            # 执行Cypher语句
            self.graph.run(cql)
            print(f"✓ 已创建 {len(relation_list)} 条 {label} 关系")


if __name__ == '__main__':
    """
    主程序入口
    执行流程:
    1. 初始化BuildGraph对象（自动解析JSON数据）
    2. 导出实体名称到文件（用于后续问答系统）
    3. 在Neo4j中创建实体节点
    4. 在Neo4j中创建关系边
    """
    print("=" * 50)
    print("电影知识图谱构建程序")
    print("=" * 50)

    # 步骤1: 初始化并解析数据
    print("\n[1/4] 正在解析JSON数据...")
    bg = BuildGraph()
    print("✓ 数据解析完成")

    # 步骤2: 导出实体文件
    print("\n[2/4] 正在导出实体文件...")
    bg.dump_entities()

    # 步骤3: 创建实体节点
    print("\n[3/4] 正在创建实体节点到Neo4j...")
    bg.create_entities()

    # 步骤4: 创建关系边
    print("\n[4/4] 正在创建关系边到Neo4j...")
    bg.create_relations()

    print("\n" + "=" * 50)
    print("知识图谱构建完成！")
    print("=" * 50)
