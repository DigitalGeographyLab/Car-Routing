CREATE EXTENSION postgis;
CREATE EXTENSION postgis_topology;
CREATE EXTENSION fuzzystrmatch; -- required for postgis_tiger_geocoder
CREATE EXTENSION postgis_tiger_geocoder;
-- this may or may not be included in your package
-- but if included allows 
-- you to use the alternative pagc_normalize_addresss function of postgis_tiger_geocoder;
CREATE EXTENSION address_standardizer;

-- a sample address standardizer rule set targetted for USA data
CREATE EXTENSION address_standardizer_data_us;


-- You will also be able to do
CREATE EXTENSION postgis_sfcgal;

    ALTER EXTENSION postgis UPDATE TO "2.3.3";

CREATE EXTENSION pgrouting;

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

commit

SELECT PostGIS_full_version();