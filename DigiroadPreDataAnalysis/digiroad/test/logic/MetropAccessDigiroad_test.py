import os
import unittest

from digiroad.carRoutingExceptions import NotWFSDefinedException, NotURLDefinedException
from digiroad.connection import FileActions
from digiroad.connection import WFSServiceProvider
from digiroad.entities import Point
from digiroad.logic.MetropAccessDigiroad import MetropAccessDigiroadApplication
from digiroad.util import CostAttributes, getEnglishMeaning


class MetropAccessDigiroadTest(unittest.TestCase):
    def setUp(self):
        self.metroAccessDigiroad = MetropAccessDigiroadApplication()
        self.wfsServiceProvider = WFSServiceProvider(wfs_url="http://localhost:8080/geoserver/wfs?",
                                                     nearestVertexTypeName="tutorial:dgl_nearest_vertex",
                                                     nearestCarRoutingVertexTypeName="tutorial:dgl_nearest_car_routable_vertex",
                                                     shortestPathTypeName="tutorial:dgl_shortest_path",
                                                     outputFormat="application/json")
        self.fileActions = FileActions()
        self.dir = os.getcwd()

    def test_givenNoneWFSService_Then_ThrowError(self):
        self.assertRaises(NotWFSDefinedException, self.metroAccessDigiroad.calculateTotalTimeTravel, None, "", "")

    def test_givenEmtpyURL_Then_ThrowError(self):
        inputCoordinatesURL = None
        outputFolderFeaturesURL = None
        self.assertRaises(NotURLDefinedException, self.metroAccessDigiroad.calculateTotalTimeTravel,
                          self.wfsServiceProvider,
                          inputCoordinatesURL,
                          outputFolderFeaturesURL)

    def test_givenAPoint_retrieveEuclideanDistanceToTheNearestVertex(self):
        euclideanDistanceExpected = 1.4044170756169843  # meters
        # startPoint = {
        #     "lat": 8443095.452975733,
        #     "lng": 2770620.87667954,
        #     "crs": "EPSG:3857"
        # }
        startPoint = Point(latitute=8443095.452975733,
                           longitude=2770620.87667954,
                           crs="EPSG:3857")

        nearestVertex = self.wfsServiceProvider.getNearestCarRoutableVertexFromAPoint(startPoint)
        epsgCode = nearestVertex["crs"]["properties"]["name"].split(":")[-3] + ":" + \
                   nearestVertex["crs"]["properties"]["name"].split(":")[-1]

        # endPoint = {
        #     "lat": nearestVertex["features"][0]["geometry"]["coordinates"][0][1],
        #     "lng": nearestVertex["features"][0]["geometry"]["coordinates"][0][0],
        #     "crs": epsgCode
        # }

        endPoint = Point(latitute=nearestVertex["features"][0]["geometry"]["coordinates"][0][1],
                         longitude=nearestVertex["features"][0]["geometry"]["coordinates"][0][0],
                         crs=epsgCode)

        self.assertEqual(euclideanDistanceExpected,
                         self.metroAccessDigiroad.calculateEuclideanDistance(startPoint, endPoint))

    def test_givenAMultiPointGeojson_then_returnGeojsonFeatures(self):
        inputCoordinatesURL = self.dir + '%digiroad%test%data%geojson%testPoints.geojson'.replace("%", os.sep)
        outputFolderFeaturesURL = self.dir + '%digiroad%test%data%outputFolder%'.replace("%", os.sep)
        distanceCostAttribute = CostAttributes.DISTANCE
        self.metroAccessDigiroad.calculateTotalTimeTravel(wfsServiceProvider=self.wfsServiceProvider,
                                                          inputCoordinatesGeojsonFilename=inputCoordinatesURL,
                                                          outputFolderPath=outputFolderFeaturesURL,
                                                          costAttribute=distanceCostAttribute)

        inputCoordinatesGeojson = self.fileActions.readJson(inputCoordinatesURL)
        if not outputFolderFeaturesURL.endswith(os.sep):
            geomsOutputFolderFeaturesURL = outputFolderFeaturesURL + os.sep + \
                                           "geoms" + os.sep + getEnglishMeaning(distanceCostAttribute) + os.sep
        else:
            geomsOutputFolderFeaturesURL = outputFolderFeaturesURL + "geoms" + os.sep + getEnglishMeaning(
                distanceCostAttribute) + os.sep

        outputFileList = self.readOutputFolderFiles(geomsOutputFolderFeaturesURL)

        self.assertEqual(len(inputCoordinatesGeojson["features"]), len(outputFileList))
        # outputFeaturesGeojson = self.readData.readJson(outputFeaturesURL)
        # self.assertEqual(, outputFeaturesGeojson)

    def test_givenAListOfGeojson_then_createSummary(self):
        self.maxDiff = None
        dir = self.dir + '%digiroad%test%data%geojson%metroAccessDigiroadSummaryResult.geojson'.replace("%", os.sep)
        outputFolderFeaturesURL = self.dir + '%digiroad%test%data%outputFolder%'.replace("%", os.sep)

        expecterResult = self.fileActions.readJson(dir)
        self.metroAccessDigiroad.createSummary(outputFolderFeaturesURL,
                                               CostAttributes.DISTANCE, "metroAccessDigiroadSummary.geojson")

        summaryOutputFolderFeaturesURL = outputFolderFeaturesURL + os.sep + "summary" + os.sep
        summaryResult = self.fileActions.readJson(
            summaryOutputFolderFeaturesURL + getEnglishMeaning(
                CostAttributes.DISTANCE) + "_metroAccessDigiroadSummary.geojson")

        self.assertEqual(expecterResult, summaryResult)

    def readOutputFolderFiles(self, outputFeaturesURL):
        outputFileList = []
        for file in os.listdir(outputFeaturesURL):
            if file.endswith(".geojson"):
                outputFileList.append(file)

        return outputFileList

    def test_calculateEuclideanDistanceToTheNearestVertex(self):
        euclideanDistanceExpected = 307.99402311696525  # meters
        # startPoint = {
        #     "lat": 8443095.452975733,
        #     "lng": 2770620.87667954,
        #     "crs": "EPSG:3857"
        # }
        startPoint = Point(latitute=60.19602778395168,
                           longitude=24.916477203369144,
                           crs="EPSG:4326")
        newStartPoint = self.metroAccessDigiroad.transformPoint(startPoint, targetEPSGCode="epsg:3857")

        nearestVertex = self.wfsServiceProvider.getNearestCarRoutableVertexFromAPoint(newStartPoint)
        epsgCode = nearestVertex["crs"]["properties"]["name"].split(":")[-3] + ":" + \
                   nearestVertex["crs"]["properties"]["name"].split(":")[-1]

        # endPoint = {
        #     "lat": nearestVertex["features"][0]["geometry"]["coordinates"][0][1],
        #     "lng": nearestVertex["features"][0]["geometry"]["coordinates"][0][0],
        #     "crs": epsgCode
        # }

        endPoint = Point(latitute=nearestVertex["features"][0]["geometry"]["coordinates"][0][1],
                         longitude=nearestVertex["features"][0]["geometry"]["coordinates"][0][0],
                         crs=epsgCode)

        self.assertEqual(euclideanDistanceExpected,
                         self.metroAccessDigiroad.calculateEuclideanDistance(newStartPoint, endPoint))
