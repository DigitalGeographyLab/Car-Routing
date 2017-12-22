import json

import psycopg2
import geopandas as gpd

from digiroad.util import getConfigurationProperties, GPD_CRS


class PostgisServiceProvider(object):
    def __init__(self, epsgCode="EPSG:3857"):
        self.epsgCode = epsgCode

    def getConnection(self):
        """
        Creates a new connection to the pg_database

        :return: New connection.
        """
        config = getConfigurationProperties(section="DATABASE_CONFIG")
        con = psycopg2.connect(database=config["database_name"], user=config["user"], password=config["password"],
                               host=config["host"])
        return con

    def executePostgisQuery(self, sql):
        """
        Given a PG_SQL execute the query and retrieve the attributes and its respective geometries.

        :param sql: Postgis SQL sentence.
        :return: Sentence query results.
        """
        con = self.getConnection()

        df = gpd.GeoDataFrame.from_postgis(sql, con, geom_col='geom', crs=GPD_CRS.PSEUDO_MERCATOR)

        jsonResult = df.to_json()
        newJson = json.loads(jsonResult)
        newJson["crs"] = {
            "properties": {
                "name": "urn:ogc:def:crs:%s" % (GPD_CRS.PSEUDO_MERCATOR["init"].replace(":", "::"))
            },
            "type": "name"
        }
        return newJson

    def getTotalShortestPathCostOneToOne(self, startVertexID, endVertexID, costAttribute):
        """
        Using the power of pgr_Dijsktra algorithm this function calculate the total routing cost for a pair of points.

        :param startVertexID: Initial Vertex to calculate the shortest path.
        :param endVertexID: Last Vertex to calculate the shortest path.
        :param costAttribute: Impedance/cost to measure the weight of the route.
        :return: Shortest path summary json.
        """
        sql = "SELECT " \
              "s.id AS start_vertex_id," \
              "e.id  AS end_vertex_id," \
              "r.agg_cost as total_time," \
              "ST_MakeLine(s.the_geom, e.the_geom) AS geom " \
              "FROM(" \
              "SELECT * " \
              "FROM pgr_dijkstraCost(" \
              "\'SELECT id::integer, source::integer, target::integer, %s::double precision AS cost, " \
              "(CASE  " \
              "WHEN liikennevi = 2 OR liikennevi = 3  " \
              "THEN %s " \
              "ELSE -1 " \
              "END)::double precision AS reverse_cost " \
              "FROM edges_noded\', %s, %s, true)) as r," \
              "edges_noded_vertices_pgr AS s," \
              "edges_noded_vertices_pgr AS e " \
              "WHERE " \
              "s.id = r.start_vid " \
              "and e.id = r.end_vid " \
              "GROUP BY " \
              "s.id, e.id, r.agg_cost" % (
                  costAttribute, costAttribute, startVertexID, endVertexID)

        return self.executePostgisQuery(sql)

    def getTotalShortestPathCostManyToOne(self, startVertexesID=[], endVertexID=None, costAttribute=None):
        """
        Using the power of pgr_Dijsktra algorithm this function calculate the total routing cost from a set of point to a single point.

        :param startVertexesID: Set of initial vertexes to calculate the shortest path.
        :param endVertexID: Last Vertex to calculate the shortest path.
        :param costAttribute: Impedance/cost to measure the weight of the route.
        :return: Shortest path summary json.
        """
        sql = "SELECT " \
              "s.id AS start_vertex_id," \
              "e.id  AS end_vertex_id," \
              "r.agg_cost as total_time," \
              "ST_MakeLine(s.the_geom, e.the_geom) AS geom " \
              "FROM(" \
              "SELECT * " \
              "FROM pgr_dijkstraCost(" \
              "\'SELECT id::integer, source::integer, target::integer, %s::double precision AS cost, " \
              "(CASE  " \
              "WHEN liikennevi = 2 OR liikennevi = 3  " \
              "THEN %s " \
              "ELSE -1 " \
              "END)::double precision AS reverse_cost " \
              "FROM edges_noded\', ARRAY[%s], %s)) as r," \
              "edges_noded_vertices_pgr AS s," \
              "edges_noded_vertices_pgr AS e " \
              "WHERE " \
              "s.id = r.start_vid " \
              "and e.id = r.end_vid " \
              "GROUP BY " \
              "s.id, e.id, r.agg_cost" % (
                  costAttribute, costAttribute, ",".join(map(str, startVertexesID)), endVertexID)

        return self.executePostgisQuery(sql)

    def getTotalShortestPathCostOneToMany(self, startVertexID=None, endVertexesID=[], costAttribute=None):
        """
        Using the power of pgr_Dijsktra algorithm this function calculate the total routing cost from a set of point to a single point.

        :param startVertexID: Initial vertexes to calculate the shortest path.
        :param endVertexesID: Set of ending vertexes to calculate the shortest path.
        :param costAttribute: Impedance/cost to measure the weight of the route.
        :return: Shortest path summary json.
        """
        sql = "SELECT " \
              "s.id AS start_vertex_id," \
              "e.id  AS end_vertex_id," \
              "r.agg_cost as total_time," \
              "ST_MakeLine(s.the_geom, e.the_geom) AS geom " \
              "FROM(" \
              "SELECT * " \
              "FROM pgr_dijkstraCost(" \
              "\'SELECT id::integer, source::integer, target::integer, %s::double precision AS cost, " \
              "(CASE  " \
              "WHEN liikennevi = 2 OR liikennevi = 3  " \
              "THEN %s " \
              "ELSE -1 " \
              "END)::double precision AS reverse_cost " \
              "FROM edges_noded\', %s, ARRAY[%s])) as r," \
              "edges_noded_vertices_pgr AS s," \
              "edges_noded_vertices_pgr AS e " \
              "WHERE " \
              "s.id = r.start_vid " \
              "and e.id = r.end_vid " \
              "GROUP BY " \
              "s.id, e.id, r.agg_cost" % (
                  costAttribute, costAttribute, startVertexID, ",".join(map(str, endVertexesID)))

        return self.executePostgisQuery(sql)

    def getTotalShortestPathCostManyToMany(self, startVertexesID=[], endVertexesID=[], costAttribute=None):
        """
        Using the power of pgr_Dijsktra algorithm this function calculate the total routing cost from a set of point to a single point.

        :param startVertexesID: Set of initial vertexes to calculate the shortest path.
        :param endVertexesID: Set of ending vertexes to calculate the shortest path.
        :param costAttribute: Impedance/cost to measure the weight of the route.
        :return: Shortest path summary json.
        """
        sql = "SELECT " \
              "s.id AS start_vertex_id," \
              "e.id  AS end_vertex_id," \
              "r.agg_cost as total_time," \
              "ST_MakeLine(s.the_geom, e.the_geom) AS geom " \
              "FROM(" \
              "SELECT * " \
              "FROM pgr_dijkstraCost(" \
              "\'SELECT id::integer, source::integer, target::integer, %s::double precision AS cost, " \
              "(CASE  " \
              "WHEN liikennevi = 2 OR liikennevi = 3  " \
              "THEN %s " \
              "ELSE -1 " \
              "END)::double precision AS reverse_cost " \
              "FROM edges_noded\', ARRAY[%s], ARRAY[%s])) as r," \
              "edges_noded_vertices_pgr AS s," \
              "edges_noded_vertices_pgr AS e " \
              "WHERE " \
              "s.id = r.start_vid " \
              "and e.id = r.end_vid " \
              "GROUP BY " \
              "s.id, e.id, r.agg_cost" % (
                  costAttribute, costAttribute, ",".join(map(str, startVertexesID)), ",".join(map(str, endVertexesID)))

        return self.executePostgisQuery(sql)

    def getEPSGCode(self):
        return self.epsgCode
