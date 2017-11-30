import unittest
import os

from digiroad.carRoutingExceptions import IncorrectGeometryTypeException
from digiroad.connection import WFSServiceProvider, FileActions
from digiroad.util import CostAttributes


class WFSServiceProviderTest(unittest.TestCase):
    def setUp(self):
        self.wfsServiceProvider = WFSServiceProvider(wfs_url="http://localhost:8080/geoserver/wfs?",
                                                     nearestVertexTypeName="tutorial:dgl_nearest_vertex",
                                                     shortestPathTypeName="tutorial:dgl_shortest_path",
                                                     outputFormat="application/json")
        self.fileActions = FileActions()
        self.dir = os.getcwd()

    def test_givenA_URL_then_returnJsonObject(self):
        dir = self.dir + '/digiroad/test/data/geojson/testPoints.geojson'
        self.assertIsNotNone(self.fileActions.readMultiPointJson(dir))

    def test_givenAGeoJson_then_attributeDataMustExist(self):
        dir = self.dir + '/digiroad/test/data/geojson/testPoints.geojson'
        multiPoints = self.fileActions.readMultiPointJson(dir)
        self.assertIsNotNone(multiPoints["data"])

    def test_givenAGeoJsonWithAttributeData_then_attributeFeaturesMustExist(self):
        dir = self.dir + '/digiroad/test/data/geojson/testPoints.geojson'
        multiPoints = self.fileActions.readMultiPointJson(dir)
        self.assertIsNotNone(multiPoints["data"]["features"])

    def test_givenAnEmptyGeoJson_then_allowed(self):
        dir = self.dir + '/digiroad/test/data/geojson/testEmpty.geojson'
        multiPoints = self.fileActions.readMultiPointJson(dir)
        self.assertEquals(0, len(multiPoints["data"]["features"]))

    def test_eachFeatureMustBeMultiPointType_IfNot_then_throwNotMultiPointGeometryError(self):
        dir = self.dir + '/digiroad/test/data/geojson/testNotMultiPointGeometry.geojson'
        self.assertRaises(IncorrectGeometryTypeException, self.fileActions.readMultiPointJson, dir)

    def test_givenAPairOfPoints_retrieveSomething(self):
        point_coordinates = {
            "lat": 60.1836272547957,
            "lng": 24.929379456878265
        }
        self.assertIsNotNone(self.wfsServiceProvider.getNearestVertextFromAPoint(point_coordinates))

    def test_givenAPoint_retrieveNearestVertexGeojson(self):
        point_coordinates = {  # EPSG:3857
            "lat": 8443095.452975733,
            "lng": 2770620.87667954
        }

        nearestVertexGeojson = self.readNearestVertextGeojsonExpectedResponse()

        self.assertEqual(nearestVertexGeojson, self.wfsServiceProvider.getNearestVertextFromAPoint(point_coordinates))

    def test_givenAPairOfPoints_then_retrieveTheShortestPath(self):
        self.maxDiff = None

        shortestPathGeojson = self.readShortestPathGeojsonExpectedResponse()
        for feature in shortestPathGeojson["features"]:
            if feature["id"]:
                del feature["id"]

        shortestPathResult = self.wfsServiceProvider.getShortestPath(startVertexId=106290, endVertexId=96275, cost=CostAttributes.DISTANCE)
        for feature in shortestPathResult["features"]:
            if feature["id"]:
                del feature["id"]

        self.assertDictEqual(shortestPathGeojson,
                             shortestPathResult)

    def readNearestVertextGeojsonExpectedResponse(self):
        fileDir = self.dir + '/digiroad/test/data/geojson/nearestVertextResponse.geojson'
        nearestVertexGeojson = self.fileActions.readJson(fileDir)
        return nearestVertexGeojson

    def readShortestPathGeojsonExpectedResponse(self):
        fileDir = self.dir + '/digiroad/test/data/geojson/shortestPathResponse.geojson'
        shortestPathGeojson = self.fileActions.readJson(fileDir)
        return shortestPathGeojson
