import unittest

import os

from digiroad.logic.MetropAccessDigiroad import MetropAccessDigiroadApplication
from digiroad.carRoutingExceptions import NotWFSDefinedException, NotURLDefinedException
from digiroad.connection import WFSServiceProvider

from digiroad.connection import FileActions
from digiroad.util import CostAttributes, getEnglishMeaning


class MetropAccessDigiroadTest(unittest.TestCase):
    def setUp(self):
        self.metroAccessDigiroad = MetropAccessDigiroadApplication()
        self.wfsServiceProvider = WFSServiceProvider(wfs_url="http://localhost:8080/geoserver/wfs?",
                                                     nearestVertexTypeName="tutorial:dgl_nearest_vertex",
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
            geomsOutputFolderFeaturesURL = outputFolderFeaturesURL + "geoms" + os.sep + getEnglishMeaning(distanceCostAttribute) + os.sep

        outputFileList = self.readOutputFolderFiles(geomsOutputFolderFeaturesURL)

        self.assertEqual(len(inputCoordinatesGeojson["data"]["features"]), len(outputFileList))
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
            summaryOutputFolderFeaturesURL + getEnglishMeaning(CostAttributes.DISTANCE) + "_metroAccessDigiroadSummary.geojson")

        self.assertEqual(expecterResult, summaryResult)

    def readOutputFolderFiles(self, outputFeaturesURL):
        outputFileList = []
        for file in os.listdir(outputFeaturesURL):
            if file.endswith(".geojson"):
                outputFileList.append(file)

        return outputFileList
