from config import *
import re

class GraphQA():
    def __init__(self):
        pass

    def query(self, text):
        slots = self.get_mention_slots(text)
        print(slots)

    def get_mention_slots(self, text):
        entities = self.parse_mention_entities(text)

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
        print(attributes)
        return {
            '%ENT%': entities,
            '%ATT%': attributes,
            '%REL%': relations
        }

if __name__ == '__main__':
    graph_qa = GraphQA()
    answer = graph_qa.query('霸王别姬的片长？')
    answer = graph_qa.query('霸王别姬是谁主演的？')