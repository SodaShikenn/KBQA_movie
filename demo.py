from py2neo import Graph

NEO4J_URI='neo4j+s://ce7d909d.databases.neo4j.io'
NEO4J_USERNAME='neo4j'
NEO4J_PASSWORD='xJ9wCJYoBYyfZAldtl60l1RzQyVnXHm73qfmIRKjDMw'

graph = Graph(NEO4J_URI, auth = (NEO4J_USERNAME, NEO4J_PASSWORD))

# cql = '''
# CREATE (:Person {name:'周星驰', age:61, gender:'男'})
# CREATE (:Person {name:'张国荣', age:46, gender:'男'})
# CREATE (:Movie {name:'功夫', 评分:8.9, 上映时间:'2004-12-23'})
# CREATE (:Movie {name:'家有喜事', 评分:8.5, 上映时间:'1992-01-25'})
# '''
# graph.run(cql)

# cql = '''
# MATCH (m:Movie {name:'功夫'}), (n:Movie {name:'家有喜事'})
# MATCH (p:Person {name:'周星驰'}), (q:Person {name:'张国荣'})
# CREATE (m)-[:ACTOR {name:'主演'}]->(p), (m)-[:DIRECTOR {name:'导演'}]->(p), (m)-[:WRITER {name:'编剧'}]->(p)
# CREATE (n)-[:ACTOR {name:'主演'}]->(p), (n)-[:ACTOR {name:'主演'}]->(q) 
# '''
# graph.run(cql)

# cql = '''
# MATCH (n {name:'周星驰'}) return n.age as RES
# '''
# graph.run(cql)

# cql = '''
# MATCH (n {name:'家有喜事'})-[:ACTOR]->(m)
# RETURN SUBSTRING(REDUCE(s = '', x IN COLLECT(m.name) | s + ' / ' + x), 3) AS RES
# '''
# graph.run(cql)

cql = '''
MATCH (n {name:'功夫'})-[rel]->(m {name:'周星驰'})
RETURN SUBSTRING(REDUCE(s = '', x IN COLLECT(rel.name) | s + ' / ' + x), 3) AS RES
'''

result = graph.run(cql).data()
print(result[0])