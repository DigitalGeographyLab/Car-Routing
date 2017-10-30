SELECT DISTINCT(surface) from edges_noded;

SELECT id::integer, source::integer, target::integer, time::double precision AS cost FROM edges_noded
LIMIT 100

SELECT
  id1 AS vertex,
  id2 AS edge,
  cost
FROM pgr_dijkstra('SELECT id::integer, source::integer, target::integer, time::double precision AS cost FROM edges_noded', 1000, 757, false, false)
ORDER BY seq;

SELECT
  e.old_id,
  e.name,
  e.type,
  e.oneway,
  e.time AS time,
  e.distance AS distance
FROM
  pgr_dijkstra('SELECT id::integer, source::integer, target::integer, time::double precision AS cost, (CASE oneway WHEN ''yes'' THEN -1 ELSE time END)::double precision AS reverse_cost FROM edges_noded', 1000, 757, true, true) AS r,
  edges_noded AS e
WHERE r.id2 = e.id;

rollback
commit

