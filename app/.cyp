// schema.cypher
CREATE CONSTRAINT IF NOT EXISTS
ON (p:Publication) ASSERT p.id IS UNIQUE;

CREATE CONSTRAINT IF NOT EXISTS
ON (m:Mission) ASSERT m.name IS UNIQUE;

CREATE CONSTRAINT IF NOT EXISTS
ON (o:Organism) ASSERT o.name IS UNIQUE;

CREATE CONSTRAINT IF NOT EXISTS
ON (s:System) ASSERT s.name IS UNIQUE;

// load.cypher
USING PERIODIC COMMIT 1000
LOAD CSV WITH HEADERS FROM 'file:///SB_publication_PMC.csv' AS row
MERGE (p:Publication {id: row.id})
SET p.title = row.title,
    p.year = toInteger(row.year),
    p.abstract = row.abstract,
    p.url = row.url;

WITH row, p
WHERE row.mission <> ''
MERGE (m:Mission {name: row.mission})
MERGE (p)-[:INVOLVES_MISSION]->(m);

WITH row, p
WHERE row.organism <> ''
MERGE (o:Organism {name: row.organism})
MERGE (p)-[:STUDIES_ORGANISM]->(o);

WITH row, p
WHERE row.system <> ''
MERGE (s:System {name: row.system})
MERGE (p)-[:TARGETS_SYSTEM]->(s);

WITH row, p
UNWIND split(row.keywords, ';') AS kw
WITH p, trim(kw) AS keyword
WHERE keyword <> ''
MERGE (k:Keyword {name: keyword})
MERGE (p)-[:TAGGED_WITH]->(k);