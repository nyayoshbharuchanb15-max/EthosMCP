// Seed data for Provenance Graph
MERGE (m:Model {id: 'base-llm-01', name: 'Base LLM v1', type: 'Foundation Model'})
MERGE (d:Dataset {id: 'clean-text-v2', name: 'Clean Text Corpus', source: 'Internal-Curated'})
MERGE (c:Component {id: 'tokenizer-x', name: 'Custom Tokenizer', license: 'MIT'})

MERGE (d)-[:USED_FOR_TRAINING]->(m)
MERGE (c)-[:PART_OF]->(m)
