import unittest

import os

from src.digiroad.logic.MetropAccessDigiroad import MetropAccessDigiroadApplication
from src.digiroad.carRoutingExceptions import NotWFSDefinedException, NotURLDefinedException
from src.digiroad.connection import WFSServiceProvider

from src.digiroad.connection import FileActions


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
        inputCoordinatesURL = self.dir + '/src/test/data/geojson/testPoints.geojson'
        outputFolderFeaturesURL = self.dir + '/src/test/data/outputFolder/'
        self.metroAccessDigiroad.calculateTotalTimeTravel(wfsServiceProvider=self.wfsServiceProvider,
                                                          inputCoordinatesGeojsonFilename=inputCoordinatesURL,
                                                          outputFolderPath=outputFolderFeaturesURL)

        inputCoordinatesGeojson = self.fileActions.readJson(inputCoordinatesURL)
        outputFileList = self.readOutputFolderFiles(outputFolderFeaturesURL)

        self.assertEqual(len(inputCoordinatesGeojson["data"]["features"]), len(outputFileList))
        # outputFeaturesGeojson = self.readData.readJson(outputFeaturesURL)
        # self.assertEqual(, outputFeaturesGeojson)

    def test_givenAListOfGeojson_then_createSummary(self):
        self.maxDiff = None
        dir = self.dir + '/src/test/data/geojson/metroAccessDigiroadSummaryResult.geojson'
        outputFolderFeaturesURL = self.dir + '/src/test/data/outputFolder/'

        expecterResult = self.fileActions.readJson(dir)
        self.metroAccessDigiroad.createSummary(outputFolderFeaturesURL, "metroAccessDigiroadSummary.geojson")

        summaryResult = self.fileActions.readJson(outputFolderFeaturesURL + "metroAccessDigiroadSummary.geojson")

        self.assertEqual(expecterResult, summaryResult)

    def readOutputFolderFiles(self, outputFeaturesURL):
        outputFileList = []
        for file in os.listdir(outputFeaturesURL):
            if file.endswith(".geojson"):
                outputFileList.append(file)

        return outputFileList
