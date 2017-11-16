## Required

To be able to upload the data from OSM/PBF files it is necessary that the database has installed the `postgis` and `hstore` extensions.

```sql
CREATE DATABASE mydatabase;

CREATE EXTENSION postgis; 
CREATE EXTENSION hstore; -- osm2pgsql
```