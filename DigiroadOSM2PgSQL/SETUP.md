## Required

To be able to upload the data from OSM/PBF files it is necessary that the database has installed the `postgis` and `hstore` extensions.

### Osmosis Linux [installation][osmosis-ins]
```
    $ wget http://bretth.dev.openstreetmap.org/osmosis-build/osmosis-latest.tgz
    $ mkdir osmosis
    $ mv osmosis-latest.tgz osmosis
    $ cd osmosis
    $ tar xvfz osmosis-latest.tgz
    $ rm osmosis-latest.tgz
    $ chmod a+x bin/osmosis
    $ bin/osmosis
```

### Imposm3 
```
    $ wget https://imposm.org/static/rel/imposm3-0.4.0dev-20170519-3f00374-linux-x86-64.tar.gz
    $ tar -C /opt/codes/ -xzf imposm3-0.4.0dev-20170519-3f00374-linux-x86-64.tar.gz
    $ cp -R imposm3-0.4.0dev-20170519-3f00374-linux-x86-64 imposm3
    $ rm -R imposm3-0.4.0dev-20170519-3f00374-linux-x86-64
    
```

### osm2pgsql 

Follow the instructions given in [here][osm2pgsql]

## Installation

```
    $ git clone git@github.com:DigitalGeographyLab/Car-Routing.git
    $ cd DigiroadOSM2PgSQL
```

### Database setup
```sql
CREATE DATABASE mydatabase;

CREATE EXTENSION postgis; 
CREATE EXTENSION hstore; -- osm2pgsql
```

### Setup configuration file 
(./resources/configuration.properties):

```
[OSM2PGSQL_CONFIG]
osm2pgsqlStyle=<default.style>
mapping=<.imposm3-mapping.json>
databasename=<databasename>
username=<username>
password=<password>
hostname=localhost
port=5432
```

## Run

    $   /opt/anaconda3/bin/./python -m digiroad -i http://download.geofabrik.de/europe/finland-latest.osm.pbf -d car_routing -o /home/jeisonle/share/ -l 24.59 -r 25.24 -t 60.35 -b 60.11

[osmosis-ins]: http://wiki.openstreetmap.org/wiki/Osmosis/Installation#Linux
[osm2pgsql]: https://github.com/openstreetmap/osm2pgsql/blob/master/README.md#building