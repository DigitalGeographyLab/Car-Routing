# Car-Routing
Repository for developing the car routing using OS GIS.

## Road network routing existing tools:

### [pgRouting](http://pgrouting.org/)
* All Pairs Shortest Path, Johnson’s Algorithm
* All Pairs Shortest Path, Floyd-Warshall Algorithm
* Shortest Path A*
* Bi-directional Dijkstra Shortest Path
* Bi-directional A* Shortest Path
* Shortest Path Dijkstra
* Driving Distance
* K-Shortest Path, Multiple Alternative Paths
* K-Dijkstra, One to Many Shortest Path
* Traveling Sales Person
* Turn Restriction Shortest Path (TRSP)
* Written in PL/SQL, an extension for PostGIS/PostgreSQL

⋅⋅⋅Data convertor:
* [shp2pgrsql](http://pgrouting.org/docs/howto/shapefiles.html) SHP files to PosgreSQL
* [osm2pgrouting](https://github.com/pgRouting/osm2pgrouting) or [osm2postgis](http://osm2postgis.sourceforge.net/) OSM files to PosgreSQL
* [Osmosis](https://github.com/openstreetmap/osmosis)

⋅⋅⋅Tutorial:
* How to implement a routing application using: pgRouting, Open Street Map and GeoServer. [Here the tutorial](http://workshops.boundlessgeo.com/tutorial-routing/)
* How to populate OpenStreetMap database. [Configuration](https://github.com/openstreetmap/openstreetmap-website/blob/master/CONFIGURE.md)
* Open Street Planet Data [http://planet.openstreetmap.org/](http://planet.openstreetmap.org/)

### [Routing KIT](https://github.com/RoutingKit/RoutingKit)
* Customizable Contraction Hierarchies
* Written in C++

### [PyrouteLib](http://wiki.openstreetmap.org/wiki/PyrouteLib)
* A*
* Written in Python

### [Graphhopper](https://github.com/graphhopper/graphhopper)
* Dijkstra
* A* (bidirectional variants)
* Contraction Hierarchies
* Written in Java

### [Routing Machine - OSRM](http://project-osrm.org/docs/v5.10.0/api/#intersection-object)
* Contraction Hierarchies (CH)
* Multi-Level Dijkstra (MLD)
* Written in C++
* Web Services

### [OptaPlanner](https://www.optaplanner.org/) (TSP and Delivery)
* Constraint satisfaction solver
* Written in Java

## Digiroad Pre-analysis Tool

[How to use](.github/src/SETUP.md). 
