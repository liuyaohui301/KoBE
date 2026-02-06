MATCH (m:Measurement)-[r1:MEASURES]->(c:Component)
MATCH (ctx:Context)-[r2:SUPPLIES]->(m)
MATCH (m)-[r3:ESTIMATES]->(s:State)
OPTIONAL MATCH (ctx)-[r4:DEGRADES]->(c)
WITH c, ctx, m, s, r1, r2, r3, r4, apoc.convert.fromJsonMap(m.summary) AS summary
WHERE c.chemistry = 'NMC'
  AND c.ratedCapacity_Ah = 2.0
  AND ctx.temperature_C >= 0.0 AND ctx.temperature_C <= 0.0
  AND ctx.lifeStage = 'early'
  AND ctx.operatingSubphase = 'cruise'
  AND s.stateType = 'SOC'
  AND summary.voltage_v.start >= 3.50 AND summary.voltage_v.start <= 4.20
  AND summary.voltage_v.end >= 3.50 AND summary.voltage_v.end <= 4.20
  AND summary.voltage_v.mean >= 3.40 AND summary.voltage_v.mean <= 4.20
  AND summary.current_a.start >= -2.00 AND summary.current_a.start <= 2.00
  AND summary.current_a.end >= -2.00 AND summary.current_a.end <= 2.00
  AND summary.current_a.mean >= -2.00 AND summary.current_a.mean <= 2.00
RETURN c, ctx, m, s, r1, r2, r3, r4
LIMIT 3