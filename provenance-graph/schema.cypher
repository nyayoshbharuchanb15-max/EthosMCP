// Provenance Graph Schema
CREATE CONSTRAINT IF NOT EXISTS FOR (m:Model) REQUIRE m.id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (d:Dataset) REQUIRE d.id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (c:Component) REQUIRE c.id IS UNIQUE;

// Lineage Relationships
// (Dataset)-[:USED_FOR_TRAINING]->(Model)
// (Component)-[:PART_OF]->(Model)
// (Model)-[:DERIVED_FROM]->(Model)
