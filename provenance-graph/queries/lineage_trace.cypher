// Trace lineage for a specific model
MATCH (m:Model {id: $model_id})<-[r:USED_FOR_TRAINING|PART_OF*]-(source)
RETURN m.name as model, type(r[0]) as relationship, source.name as source_name, source.type as source_type
