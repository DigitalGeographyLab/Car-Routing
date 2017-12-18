import os
import unittest

from digiroad.carRoutingExceptions import NotWFSDefinedException, NotURLDefinedException
from digiroad.connection import FileActions
from digiroad.connection import WFSServiceProvider
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
        testPolygonsURL = None

        self.assertRaises(NotURLDefinedException,
                          self.metroAccessDigiroad.calculateTotalTimeTravel,
                          self.wfsServiceProvider,
                          inputCoordinatesURL,
                          outputFolderFeaturesURL,
                          testPolygonsURL)

    @unittest.skip("")  # about 13 m for 12 points (132 possible paths)
    def test_givenAMultiPointGeojson_then_returnGeojsonFeatures(self):
        inputCoordinatesURL = self.dir + '%digiroad%test%data%geojson%reititinTestPoints.geojson'.replace("%", os.sep)
        outputFolderFeaturesURL = self.dir + '%digiroad%test%data%outputFolder%'.replace("%", os.sep)

        distanceCostAttribute = CostAttributes.DISTANCE
        self.metroAccessDigiroad.calculateTotalTimeTravel(wfsServiceProvider=self.wfsServiceProvider,
                                                          startCoordinatesGeojsonFilename=inputCoordinatesURL,
                                                          endCoordinatesGeojsonFilename=inputCoordinatesURL,
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

        totalCombinatory = len(inputCoordinatesGeojson["features"]) * len(inputCoordinatesGeojson["features"]) - len(
            inputCoordinatesGeojson["features"])
        self.assertEqual(totalCombinatory, len(outputFileList))

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
