import unittest
import os

from src.digiroad.carRoutingExceptions import NotMultiPointGeometryException
from src.digiroad.connection import ReadData


class ReadDataTest(unittest.TestCase):
    def setUp(self):
        self.readData = ReadData(wfs_url="http://localhost:8080/geoserver/wfs?",
                                 nearestVertexTypeName="tutorial:dgl_nearest_vertex",
                                 shortestPathTypeName="tutorial:dgl_shortest_path",
                                 outputFormat="application/json")
        self.dir = os.getcwd()

    def test_givenA_URL_then_returnJsonObject(self):
        dir = self.dir + '/src/test/data/geojson/testPoints.geojson'
        self.assertIsNotNone(self.readData.readMultiPointJson(dir))

    def test_givenAGeoJson_then_attributeDataMustExist(self):
        dir = self.dir + '/src/test/data/geojson/testPoints.geojson'
        multiPoints = self.readData.readMultiPointJson(dir)
        self.assertIsNotNone(multiPoints["data"])

    def test_givenAGeoJsonWithAttributeData_then_attributeFeaturesMustExist(self):
        dir = self.dir + '/src/test/data/geojson/testPoints.geojson'
        multiPoints = self.readData.readMultiPointJson(dir)
        self.assertIsNotNone(multiPoints["data"]["features"])

    def test_givenAnEmptyGeoJson_then_allowed(self):
        dir = self.dir + '/src/test/data/geojson/testEmpty.geojson'
        multiPoints = self.readData.readMultiPointJson(dir)
        self.assertEquals(0, len(multiPoints["data"]["features"]))

    def test_eachFeatureMustBeMultiPointType_IfNot_then_throwNotMultiPointGeometryError(self):
        dir = self.dir + '/src/test/data/geojson/testNotMultiPointGeometry.geojson'
        self.assertRaises(NotMultiPointGeometryException, self.readData.readMultiPointJson, dir)

    def test_givenAPairOfPoints_retrieveSomething(self):
        point_coordinates = {
            "lat": 60.1836272547957,
            "lng": 24.929379456878265
        }
        self.assertIsNotNone(self.readData.getNearestVertextFromAPoint(point_coordinates))

    def test_givenAPoint_retrieveNearestVertexGeojson(self):
        point_coordinates = {  # EPSG:3857
            "lat": 8443095.452975733,
            "lng": 2770620.87667954
        }

        nearestVertexGeojson = self.createNearestVertextGeojson()

        self.assertEqual(nearestVertexGeojson, self.readData.getNearestVertextFromAPoint(point_coordinates))

    def test_givenAPairOfPoints_then_retrieveTheShortestPath(self):
        self.maxDiff = None

        shortestPathGeojson = self.createShortestPathGeojson()
        for feature in shortestPathGeojson["features"]:
            if feature["id"]:
                del feature["id"]

        shortestPathResult = self.readData.getShortestPath(startVertexId=106290, endVertexId=96275, cost="pituus")
        for feature in shortestPathResult["features"]:
            if feature["id"]:
                del feature["id"]

        self.assertDictEqual(shortestPathGeojson,
                             shortestPathResult)

    def createNearestVertextGeojson(self):
        fileDir = self.dir + '/src/test/data/geojson/nearestVertextResponse.geojson'
        nearestVertexGeojson = self.readData.readJson(fileDir)
        return nearestVertexGeojson

    def createShortestPathGeojson(self):
        fileDir = self.dir + '/src/test/data/geojson/shortestPathResponse.geojson'
        shortestPathGeojson = self.readData.readJson(fileDir)
        return shortestPathGeojson
