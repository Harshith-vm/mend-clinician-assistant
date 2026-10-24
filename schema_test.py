import os
from neo4j import GraphDatabase

d = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', os.environ.get("NEO4J_PASSWORD", "")))

print("=== ASSOCIATED_WITH edges from EmotionalState to Disorder ===")
res = d.execute_query('''
MATCH (e:EmotionalState)-[r:ASSOCIATED_WITH]->(d:Disorder)
RETURN e.name AS emotion, d.name AS disorder, r.confidence AS conf
LIMIT 10
''', database_='therapy')
print(f"Total found: {len(res[0])}")
for r in res[0]:
    print(f"  {r['emotion']} -> {r['disorder']} (conf={r['conf']})")

print("\n=== Checking if Shame EmotionalState has any ASSOCIATED_WITH links ===")
res2 = d.execute_query('''
MATCH (e:EmotionalState) WHERE e.name = "Shame"
OPTIONAL MATCH (e)-[r]->(x)
RETURN type(r) AS rel, labels(x)[0] AS target_type, x.name AS target_name
LIMIT 10
''', database_='therapy')
for r in res2[0]:
    print(f"  {r['rel']} -> {r['target_type']}: {r['target_name']}")

print("\n=== Behaviour node names that ACTUALLY exist ===")
res3 = d.execute_query('''
MATCH (b:Behaviour) RETURN b.name
''', database_='therapy')
print([r['b.name'] for r in res3[0]])

print("\n=== Checking Emotional_Expression behaviour match ===")
res4 = d.execute_query('''
MATCH (b:Behaviour) WHERE toLower(b.name) = toLower("EmotionalExpression")
RETURN b.name
''', database_='therapy')
print("EmotionalExpression match:", [r['b.name'] for r in res4[0]])

d.close()
