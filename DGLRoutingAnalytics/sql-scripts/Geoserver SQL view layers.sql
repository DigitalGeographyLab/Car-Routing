SELECT
  min(r.seq) AS seq,
  e.old_id AS id,
  e.name,
  e.type,
  e.oneway,
  sum(e.time) AS time,
  sum(e.distance) AS distance,
  ST_Collect(e.the_geom) AS geom
FROM
  pgr_dijkstra(
   'SELECT
    id::integer,
    source::integer,
    target::integer,
    %cost%::double precision AS cost,
    (CASE oneway
      WHEN ''yes'' THEN -1
      ELSE %cost%
    END)::double precision AS reverse_cost
  FROM edges_noded', %source%, %target%, true, true) AS r,
  edges_noded AS e
WHERE
  r.id2 = e.id
GROUP BY
  e.old_id, e.name, e.type, e.oneway
  
--------------------------------------------------------------------------------------------------
  
SELECT
  v.id,
  v.the_geom,
  string_agg(distinct(e.name),',') AS name
FROM
  edges_noded_vertices_pgr AS v,
  edges_noded AS e
WHERE
  v.id = (SELECT
            id
          FROM edges_noded_vertices_pgr
          ORDER BY the_geom <-> ST_SetSRID(ST_MakePoint(%x%, %y%), 3857) LIMIT 1)
  AND (e.source = v.id OR e.target = v.id)
GROUP BY v.id, v.the_geom