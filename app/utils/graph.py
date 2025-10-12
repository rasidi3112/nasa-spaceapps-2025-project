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
                # Pastikan setiap node punya id, title, label
                node_id = str(node.get("id") or node.id)
                node_title = node.get("title") or node.get("name") or f"Node {node_id}"
                node_label = node.get("label") or list(node.labels)[0] if node.labels else "Unknown"

                nodes[node_id] = {
                    "id": node_id,
                    "title": node_title,
                    "label": node_label,
                    **dict(node)  # simpan properti lain jika ada
                }

            for rel in path.relationships:
                start_id = str(rel.start_node.get("id") or rel.start_node.id)
                end_id = str(rel.end_node.get("id") or rel.end_node.id)
                edges.append({
                    "source": start_id,
                    "target": end_id,
                    "type": rel.type,
                })

    driver.close()
    return {"nodes": list(nodes.values()), "edges": edges}
