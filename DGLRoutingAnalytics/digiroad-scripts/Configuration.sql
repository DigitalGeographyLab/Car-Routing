ALTER TABLE edges ADD source INT4;
ALTER TABLE edges ADD target INT4;

ALTER TABLE edges
  ALTER COLUMN the_geom TYPE geometry(LineString)
    USING ST_Force2D(the_geom);

SELECT pgr_createTopology('edges', 1);
SELECT pgr_nodeNetwork('edges', 1);
SELECT pgr_createTopology('edges_noded', 1);

ALTER TABLE edges_noded
  ADD COLUMN tiee_kunta numeric(9,0),
  ADD COLUMN toiminnall numeric(9,0),
  ADD COLUMN liikennevi numeric(9,0),
  ADD COLUMN pituus numeric(19,11),
  ADD COLUMN digiroa_aa numeric(19,11),
  ADD COLUMN kokopva_aa numeric(19,11),
  ADD COLUMN keskpva_aa numeric(19,11),
  ADD COLUMN ruuhka_aa numeric(19,11),
  ADD COLUMN kmh numeric(4,0);

UPDATE edges_noded AS new
SET
  tiee_kunta  = old.tiee_kunta,
  toiminnall = old.toiminnall,
  liikennevi = old.liikennevi,
  pituus = old.pituus,
  digiroa_aa = old.digiroa_aa,
  kokopva_aa = old.kokopva_aa,
  keskpva_aa = old.keskpva_aa,
  ruuhka_aa = old.ruuhka_aa,
  kmh = old.kmh
FROM edges AS old
WHERE old_id = old.id;

SELECT DISTINCT(type) from edges_noded;

ALTER TABLE edges_noded ADD distance FLOAT8;
ALTER TABLE edges_noded ADD time FLOAT8;
-- UPDATE edges_noded SET pituus = ST_Length(ST_Transform(the_geom, 4326)::geography) / 1000; --not running given that the distances was already calculated


-- when toiminnall = 10, the road segment is not routable
UPDATE edges_noded AS new
SET
  pituus = -1,
  digiroa_aa = -1,
  kokopva_aa = -1,
  keskpva_aa = -1,
  ruuhka_aa = -1,
  kmh = -1
WHERE toiminnall = 10;

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
  END;

rollback
commit
