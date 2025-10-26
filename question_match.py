from config import *
import re, json, itertools, Levenshtein

class GraphQA():
    def __init__(self):
        pass

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
                    question = self.replace_token_in_string(template['question'], combinatio_n)
                    cypher = self.replace_token_in_string(template['cypher'], combination)
                    answer = self.replace_token_in_string(template['answer'], combination)
                    valid_templates.append({'question': question, 'cypher': cypher, 'answer': answer})
        return valid_templates
    
    def compute_question_similarity(self, templates, text):
        for i, template in enumerate(templates):
            score = Levenshtein.ratio(template['question'], text)
            if score > 0.1:
                template['score'] = score
            else:
                del templates[i]
        return sorted(templates, key=lambda x:x['score'], reverse=True)


    # 调用
    def query(self, text):
        slots = self.get_mention_slots(text)
        print(slots)
        templates = self.expand_templates(slots)
        templates = self.compute_question_similarity(templates, text)
        print(templates)

if __name__ == '__main__':
    graph_qa = GraphQA()
    answer = graph_qa.query('霸王别姬的片长？')
    # answer = graph_qa.query('霸王别姬是谁主演的？')
    # answer = graph_qa.query('张国荣和霸王别姬是什么关系？')