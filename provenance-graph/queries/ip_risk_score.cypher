// Calculate IP risk score based on component licenses
MATCH (m:Model {id: $model_id})<-[:PART_OF]-(c:Component)
WITH count(c) as total_components, 
     count(CASE WHEN c.license IN ['GPL-3.0', 'AGPL-3.0'] THEN 1 END) as copyleft_count
RETURN (copyleft_count * 100.0 / total_components) as ip_risk_score
