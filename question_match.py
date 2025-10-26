from config import *
import re, json, itertools, Levenshtein
from py2neo import Graph

class GraphQA():
    def __init__(self):
        self.graph = Graph(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    def parse_mention_entities(self, text):
        with open(ENTITIES_PATH, encoding='utf-8') as file:
            entities = file.read().split('\n')
        return re.findall('|'.join(entities).replace('(', '').replace(')', ''), text)

    def parse_mention_entities(self, text):
        with open(ENTITIES_PATH, encoding='utf-8') as file:
            entities = file.read().split('\n')
        return re.findall('|'.join(entities).replace('(', '').replace(')', ''), text)

    def parse_mention_attributes(self, text):
        attrs = re.findall('|'.join(SYNONYMS_MAP['attributes'].keys()), text)
        return list(set([SYNONYMS_MAP['attributes'][attr] for attr in attrs]))

    def parse_mention_relations(self, text):
        rels = re.findall('|'.join(SYNONYMS_MAP['relations'].keys()), text)
        return list(set([SYNONYMS_MAP['relations'][rel] for rel in rels]))

    def get_mention_slots(self, text):
        entities = self.parse_mention_entities(text)
        attributes = self.parse_mention_attributes(text)
        relations = self.parse_mention_relations(text)
        return {
            '%ENT%': entities,
            '%ATT%': attributes,
            '%REL%': relations
        }

    def get_slots_combinations(self, cypher_slots, slots):
        value_combinations = []
        for k,v in cypher_slots.items():
            value_combinations.append([*itertools.permutations(slots[k], v)])
        combinations = []
        for value_combination in itertools.product(*value_combinations):
            result = {}
            for value, key in zip(value_combination, cypher_slots):
                if len(value) == 1:
                    result[key] = value[0]
                else:
                    for i in range(len(value)):
                        result[key[:-1]+str(i)+'%'] = value[i]
            combinations.append(result)
        return combinations
    
    def check_slots(self, cypher_slots, slots):
        for k, v in cypher_slots.items():
            if v > len(slots[k]):
                return False
        return True

    def replace_token_in_string(self, string, combination):
        for key, value in combination.items():
            string = string.replace(key, value)
        return string

    def expand_templates(self, slots):
        valid_templates = []
        for template in TEMPLATES:
            cypher_slots = json.loads(template['slots'])
            if self.check_slots(cypher_slots, slots):
                combinations = self.get_slots_combinations(cypher_slots, slots)
                for combination in combinations:
                    question = self.replace_token_in_string(template['question'], combination)
                    cypher = self.replace_token_in_string(template['cypher'], combination)
                    answer = self.replace_token_in_string(template['answer'], combination)
                    valid_templates.append({'question': question, 'cypher': cypher, 'answer': answer})
        return valid_templates
    
    def compute_question_similarity(self, templates, text):
        for i, template in enumerate(templates):
            score = Levenshtein.ratio(template['question'], text)
            if score > THRESHOLD:
                template['score'] = score
            else:
                del templates[i]
        return sorted(templates, key=lambda x:x['score'], reverse=True)

    def query_and_replace_answer(self, templates):
        for template in templates:
            try:
                result = self.graph.run(template['cypher']).data()[0]
                if result['RES']:
                    return self.replace_token_in_string(template['answer'], {'RES': result['RES']})
            except:
                pass

    # 调用
    def query(self, text):
        slots = self.get_mention_slots(text)
        templates = self.expand_templates(slots)
        templates = self.compute_question_similarity(templates, text)
        answer = self.query_and_replace_answer(templates)
        return answer if answer else '抱歉，没有找到答案！'


if __name__ == '__main__':
    graph_qa = GraphQA()
    answer = graph_qa.query('霸王别姬的片长？')
    print(answer)
    answer = graph_qa.query('霸王别姬是谁主演的？')
    print(answer)
    answer = graph_qa.query('张国荣和霸王别姬是什么关系？')
    print(answer)
    answer = graph_qa.query('贞子的导演是谁？')
    print(answer)
    answer = graph_qa.query('肖申克的救赎编剧有哪些？')
    print(answer)
"""
   [{'question': '霸王别姬主演过哪些电影', 
     'cypher': "MATCH (n)-[:主演]->(m {name:'霸王别姬'}) RETURN SUBSTRING(REDUCE(s = '', x IN COLLECT(n.name) | s + ' / ' + x), 3) AS RES", 
     'answer': '霸王别姬主演过的电影：RES', 
     'score': 0.5714285714285714}, 
     {'question': '霸王别姬的主演是谁/有哪些', 
      'cypher': "MATCH (n {name:'霸王别姬'})-[:主演]->(m) RETURN SUBSTRING(REDUCE(s = '', x IN COLLECT(m.name) | s + ' / ' + x), 3) AS RES", 
      'answer': '霸王别姬的主演：RES', 
      'score': 0.5217391304347826}] 
"""