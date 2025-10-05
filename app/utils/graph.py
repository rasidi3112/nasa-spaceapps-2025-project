# app/utils/graph.py
from typing import Optional
from neo4j import GraphDatabase # type: ignore

URI = "neo4j+s://your-neo4j-instance.databases.neo4j.io"
AUTH = ("neo4j", "password")

def fetch_subgraph(seed: str, depth: int, mission: Optional[str]):
    driver = GraphDatabase.driver(URI, auth=AUTH)
    query = """
    MATCH path = (p:Publication {id: $seed})-[:RELATES_TO*1..$depth]-(x)
    WHERE $mission IS NULL OR x.mission = $mission
    RETURN path
    """
    nodes = {}
    edges = []
    with driver.session() as session:
        result = session.run(query, seed=seed, depth=depth, mission=mission)
        for record in result:
            path = record["path"]
            for node in path.nodes:
                nodes[node.id] = dict(node)
            for rel in path.relationships:
                edges.append({
                    "source": rel.start_node["id"],
                    "target": rel.end_node["id"],
                    "type": rel.type,
                })
    driver.close()
    return {"nodes": list(nodes.values()), "edges": edges}