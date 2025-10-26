lst = [
    {'score': 0.55, 'question':'周星驰的导演是谁'},
    {'score': 0.4, 'question':'周星驰主演过哪些电影'},
    {'score': 0.8, 'question':'周星驰导演过哪些电影'},
]

res = sorted(lst, key=lambda x:x['score'], reverse=True)
print(res)

exit()

import Levenshtein

question = '周星驰导演过什么电影'

t_question1 = '周星驰导演过哪些电影'
t_question2 = '周星驰的导演是谁'

print(Levenshtein.ratio(question, t_question1))
print(Levenshtein.ratio(question, t_question2))

exit()

question = '%ENT%的%REL%是谁？'
combination = {'%ENT%':'霸王别姬', '%REL%':'导演'}

def replace_token_in_string(string, combination):
    for key, value in combination.items():
        string = string.replace(key, value)
    return string

res = replace_token_in_string(question, combination)
print(res)

exit()


def check_slots(cypher_slots, slots):
    for k, v in cypher_slots.items():
        if v > len(slots[k]):
            return False
    return True


cypher_slots = {
    "%ENT%": 3,
    "%REL%": 1,
}

slots = {
    "%ENT%": ['霸王别姬', '张国荣'],
    "%REL%": ['主演', '导演']
}

print(check_slots(cypher_slots, slots))
exit()

import itertools


def get_slots_combinations(cypher_slots, slots):
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

cypher_slots = {
    "%ENT%": 2,
    "%REL%": 1,
}

slots = {
    "%ENT%": ['霸王别姬', '张国荣'],
    "%REL%": ['主演', '导演']
}

result = get_slots_combinations(cypher_slots, slots)
print(result)

exit()



lst3 = [(('张国荣', '霸王别姬'), ('导演',)), (('张国荣', '霸王别姬'), ('主演',)), (('霸王别姬', '张国荣'), ('导演',)), (('霸王别姬', '张国荣'), ('主演',))]
lst4 = ['%ENT%', '%REL%']
# 期望结果：[{%ENT0%:'张国荣', %ENT1%:'霸王别姬', '%REL%':'导演'}, ...]

result = []
for item in lst3:
    dct = {}
    for value, key in zip(item, lst4):
        if len(value)==1:
            dct[key] = value[0]
        else:
            for i in range(len(value)):
                dct[key[:-1]+str(i)+'%'] = value[i]
    result.append(dct)
print(result)

exit()


import itertools


lst1 = [('张国荣', '霸王别姬'), ('霸王别姬', '张国荣')]
lst2 = [('导演',), ('主演',)]

res = itertools.product(lst1, lst2)
print(list(res))
exit()


lst = ['张国荣', '霸王别姬', '周星驰']
res = itertools.permutations(lst, 1)
print(list(res))


exit()


import re

quesiton = '霸王别姬和功夫有共同的主演吗？'

lst = ['霸王别姬', '功夫', '阿甘正传', '阿凡达(Avatar)']

res = re.findall('|'.join(lst).replace('(', '').replace(')', ''), quesiton)

print(res)

exit()


from collections import defaultdict

entity_data = defaultdict(list)
entity_data['MOVIE'].append('霸王别姬')
entity_data['PERSON'].append('张国荣')
print(entity_data['MOVIE'][0])
exit()


entity_data = {}
entity_data['MOVIE'] = []
entity_data['MOVIE'].append('霸王别姬')
entity_data['PERSON'] = []
entity_data['PERSON'].append('张国荣')
print(entity_data)
