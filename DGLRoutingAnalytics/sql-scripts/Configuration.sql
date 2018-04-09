ALTER TABLE edges ADD source INT4;
ALTER TABLE edges ADD target INT4;
--#########################################################################################
-- If getting the errors:
/*
Warning 1: Geometry to be inserted is of type 3D Measured Multi Line String, whereas the layer geometry type is 3D Measured Line String (when running org2org library).
Or
Unexpected error Geometry has Z dimension but column does not (When running pgr_createTopology())
*/
 */
ALTER TABLE edges
  ALTER COLUMN the_geom TYPE geometry(MULTILINESTRING,3857) USING ST_Force2D(the_geom) ;
--#########################################################################################

SELECT pgr_createTopology('edges', 1);

--#########################################################################################
-- No need to create a new road network, pgRouting do not distribute the cost attribute proportionally to the new segments.
-- SELECT pgr_nodeNetwork('edges', 1);
-- SELECT pgr_createTopology('edges_noded', 1);

/*ALTER TABLE edges_noded
  ADD COLUMN name VARCHAR,
  ADD COLUMN type VARCHAR,
  ADD COLUMN oneway VARCHAR,
  ADD COLUMN surface VARCHAR;

UPDATE edges_noded AS new
SET
  name = CASE WHEN old.name IS NULL THEN old.ref ELSE old.name END,
  type = old.highway,
  oneway = old.oneway,
  surface = old.surface
FROM edges AS old
WHERE new.old_id = old.id;

SELECT DISTINCT(type) from edges_noded;

ALTER TABLE edges_noded ADD distance FLOAT8;
ALTER TABLE edges_noded ADD time FLOAT8;
UPDATE edges_noded SET distance = ST_Length(ST_Transform(the_geom, 4326)::geography) / 1000;

UPDATE edges_noded SET
  time =
  CASE type
    WHEN 'steps' THEN -1
    WHEN 'path' THEN -1
    WHEN 'footway' THEN -1
    WHEN 'cycleway' THEN -1
    WHEN 'proposed' THEN -1
    WHEN 'construction' THEN -1
    WHEN 'raceway' THEN distance / 100
    WHEN 'motorway' THEN distance / 70
    WHEN 'motorway_link' THEN distance / 70
    WHEN 'trunk' THEN distance / 60
    WHEN 'trunk_link' THEN distance / 60
    WHEN 'primary' THEN distance / 55
    WHEN 'primary_link' THEN distance / 55
    WHEN 'secondary' THEN distance / 45
    WHEN 'secondary_link' THEN distance / 45
    WHEN 'tertiary' THEN distance / 45
    WHEN 'tertiary_link' THEN distance / 40
    WHEN 'unclassified' THEN distance / 35
    WHEN 'residential' THEN distance / 30
    WHEN 'living_street' THEN distance / 30
    WHEN 'service' THEN distance / 30
    WHEN 'track' THEN distance / 20
    ELSE distance / 20
  END;

UPDATE edges_noded SET
  distance =
  CASE type
    WHEN 'steps' THEN -1
    WHEN 'path' THEN -1
    WHEN 'footway' THEN -1
    WHEN 'cycleway' THEN -1
    WHEN 'proposed' THEN -1
    WHEN 'construction' THEN -1
    ELSE distance
  END;*/

-- CREATE INDEX edges_noded_vertices_pgr_gix ON edges_noded_vertices_pgr USING GIST (the_geom);
CREATE INDEX edges_vertices_pgr_gix ON edges_vertices_pgr USING GIST (the_geom);

-- The commands below are necessary to replicate the tables into the different nodes that belong to the cluster
ALTER TABLE edges DISTRIBUTE BY REPLICATION;
ALTER TABLE edges_vertices_pgr DISTRIBUTE BY REPLICATION;

--rollback
--commit