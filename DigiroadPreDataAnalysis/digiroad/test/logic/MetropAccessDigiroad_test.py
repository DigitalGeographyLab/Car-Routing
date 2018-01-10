import os
import unittest

from digiroad.carRoutingExceptions import NotWFSDefinedException, NotURLDefinedException
from digiroad.connection import WFSServiceProvider
from digiroad.connection.PostgisServiceProvider import PostgisServiceProvider
from digiroad.logic.MetropAccessDigiroad import MetropAccessDigiroadApplication
from digiroad.util import CostAttributes, getEnglishMeaning, FileActions


class MetropAccessDigiroadTest(unittest.TestCase):
    def setUp(self):
        self.wfsServiceProvider = WFSServiceProvider(wfs_url="http://localhost:8080/geoserver/wfs?",
                                                     nearestVertexTypeName="tutorial:dgl_nearest_vertex",
                                                     nearestCarRoutingVertexTypeName="tutorial:dgl_nearest_car_routable_vertex",
                                                     shortestPathTypeName="tutorial:dgl_shortest_path",
                                                     outputFormat="application/json")
        self.postgisServiceProvider = PostgisServiceProvider()
        self.metroAccessDigiroad = MetropAccessDigiroadApplication(self.wfsServiceProvider, self.postgisServiceProvider)
        self.fileActions = FileActions()
        self.dir = os.getcwd()

    def test_givenNoneWFSService_Then_ThrowError(self):
        metroAccessDigiroad = MetropAccessDigiroadApplication(None, None)
        self.assertRaises(NotWFSDefinedException, metroAccessDigiroad.calculateTotalTimeTravel, "", "", "", "")

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

    # @unittest.skip("")  # about 13 m for 12 points (132 possible paths)
    def test_givenAMultiPointGeojson_then_returnGeojsonFeatures(self):
        inputCoordinatesURL = self.dir + '%digiroad%test%data%geojson%reititinTestPoints.geojson'.replace("%", os.sep)
        outputFolderFeaturesURL = self.dir + '%digiroad%test%data%outputFolder%'.replace("%", os.sep)

        # distanceCostAttribute = CostAttributes.DISTANCE
        distanceCostAttribute = {
            "DISTANCE": CostAttributes.DISTANCE,
            "SPEED_LIMIT_TIME": CostAttributes.SPEED_LIMIT_TIME,
            "DAY_AVG_DELAY_TIME": CostAttributes.DAY_AVG_DELAY_TIME,
            "MIDDAY_DELAY_TIME": CostAttributes.MIDDAY_DELAY_TIME,
            "RUSH_HOUR_DELAY": CostAttributes.RUSH_HOUR_DELAY
        }
        self.metroAccessDigiroad.calculateTotalTimeTravel(startCoordinatesGeojsonFilename=inputCoordinatesURL,
                                                          endCoordinatesGeojsonFilename=inputCoordinatesURL,
                                                          outputFolderPath=outputFolderFeaturesURL,
                                                          costAttribute=distanceCostAttribute)

        inputCoordinatesGeojson = self.fileActions.readJson(inputCoordinatesURL)
        for key in distanceCostAttribute:
            if not outputFolderFeaturesURL.endswith(os.sep):
                geomsOutputFolderFeaturesURL = outputFolderFeaturesURL + os.sep + \
                                               "geoms" + os.sep + getEnglishMeaning(distanceCostAttribute[key]) + os.sep
            else:
                geomsOutputFolderFeaturesURL = outputFolderFeaturesURL + "geoms" + os.sep + getEnglishMeaning(
                    distanceCostAttribute[key]) + os.sep

            outputFileList = self.readOutputFolderFiles(geomsOutputFolderFeaturesURL)

            totalCombinatory = len(inputCoordinatesGeojson["features"]) * len(inputCoordinatesGeojson["features"]) - len(
                inputCoordinatesGeojson["features"])
            self.assertEqual(totalCombinatory, len(outputFileList))

    def test_givenAListOfGeojson_then_createSummary(self):
        self.maxDiff = None
        expectedJsonURL = self.dir + '%digiroad%test%data%geojson%metroAccessDigiroadSummaryResult.geojson'.replace("%",
                                                                                                                    os.sep)
        outputFolderFeaturesURL = self.dir + '%digiroad%test%data%outputFolder%'.replace("%", os.sep)

        expectedResult = self.fileActions.readJson(expectedJsonURL)
        self.metroAccessDigiroad.createSummary(outputFolderFeaturesURL,
                                               CostAttributes.DISTANCE, "metroAccessDigiroadSummary.geojson")

        summaryOutputFolderFeaturesURL = outputFolderFeaturesURL + os.sep + "summary" + os.sep
        summaryResult = self.fileActions.readJson(
            summaryOutputFolderFeaturesURL + getEnglishMeaning(
                CostAttributes.DISTANCE) + "_metroAccessDigiroadSummary.geojson")

        self.assertEqual(expectedResult, summaryResult)

    def test_givenOneStartPointGeojsonAndOneEndPointGeojson_then_createMultiPointSummary(self):
        startInputCoordinatesURL = self.dir + '%digiroad%test%data%geojson%onePoint.geojson'.replace("%", os.sep)
        endInputCoordinatesURL = self.dir + '%digiroad%test%data%geojson%anotherPoint.geojson'.replace("%", os.sep)
        outputFolderFeaturesURL = self.dir + '%digiroad%test%data%outputFolder%'.replace("%", os.sep)

        expectedJsonURL = self.dir + '%digiroad%test%data%geojson%oneToOneCostSummary.geojson'.replace("%", os.sep)

        expectedResult = self.fileActions.readJson(expectedJsonURL)

        self.metroAccessDigiroad.createMultiPointSummary(
            startCoordinatesGeojsonFilename=startInputCoordinatesURL,
            endCoordinatesGeojsonFilename=endInputCoordinatesURL,
            costAttribute=CostAttributes.DISTANCE,
            folderPath=outputFolderFeaturesURL,
            outputFilename="oneToOneCostSummary.geojson"
        )

        summaryOutputFolderFeaturesURL = outputFolderFeaturesURL + os.sep + "summary" + os.sep
        summaryResult = self.fileActions.readJson(
            summaryOutputFolderFeaturesURL + getEnglishMeaning(
                CostAttributes.DISTANCE) + "_oneToOneCostSummary.geojson")

        self.assertEqual(expectedResult, summaryResult)

    def test_givenOneStartPointGeojsonAndManyEndPointsGeojson_then_createMultiPointSummary(self):
        startInputCoordinatesURL = self.dir + '%digiroad%test%data%geojson%onePoint.geojson'.replace("%", os.sep)
        endInputCoordinatesURL = self.dir + '%digiroad%test%data%geojson%reititinTestPoints.geojson'.replace("%", os.sep)
        outputFolderFeaturesURL = self.dir + '%digiroad%test%data%outputFolder%'.replace("%", os.sep)

        expectedJsonURL = self.dir + '%digiroad%test%data%geojson%oneToManyCostSummary.geojson'.replace("%", os.sep)

        expectedResult = self.fileActions.readJson(expectedJsonURL)

        self.metroAccessDigiroad.createMultiPointSummary(
            startCoordinatesGeojsonFilename=startInputCoordinatesURL,
            endCoordinatesGeojsonFilename=endInputCoordinatesURL,
            costAttribute=CostAttributes.DISTANCE,
            folderPath=outputFolderFeaturesURL,
            outputFilename="oneToManyCostSummary.geojson"
        )

        summaryOutputFolderFeaturesURL = outputFolderFeaturesURL + os.sep + "summary" + os.sep
        summaryResult = self.fileActions.readJson(
            summaryOutputFolderFeaturesURL + getEnglishMeaning(
                CostAttributes.DISTANCE) + "_oneToManyCostSummary.geojson")

        self.assertEqual(expectedResult, summaryResult)


    def test_givenManyStartPointsGeojsonAndOneEndPointGeojson_then_createMultiPointSummary(self):
        startInputCoordinatesURL = self.dir + '%digiroad%test%data%geojson%reititinTestPoints.geojson'.replace("%", os.sep)
        endInputCoordinatesURL = self.dir + '%digiroad%test%data%geojson%onePoint.geojson'.replace("%", os.sep)
        outputFolderFeaturesURL = self.dir + '%digiroad%test%data%outputFolder%'.replace("%", os.sep)

        expectedJsonURL = self.dir + '%digiroad%test%data%geojson%manyToOneCostSummary.geojson'.replace("%", os.sep)

        expectedResult = self.fileActions.readJson(expectedJsonURL)

        self.metroAccessDigiroad.createMultiPointSummary(
            startCoordinatesGeojsonFilename=startInputCoordinatesURL,
            endCoordinatesGeojsonFilename=endInputCoordinatesURL,
            costAttribute=CostAttributes.DISTANCE,
            folderPath=outputFolderFeaturesURL,
            outputFilename="manyToOneCostSummary.geojson"
        )

        summaryOutputFolderFeaturesURL = outputFolderFeaturesURL + os.sep + "summary" + os.sep
        summaryResult = self.fileActions.readJson(
            summaryOutputFolderFeaturesURL + getEnglishMeaning(
                CostAttributes.DISTANCE) + "_manyToOneCostSummary.geojson")

        self.assertEqual(expectedResult, summaryResult)

    def test_givenManyStartPointsGeojsonAndManyEndPointsGeojson_then_createMultiPointSummary(self):
        startInputCoordinatesURL = self.dir + '%digiroad%test%data%geojson%reititinTestPoints.geojson'.replace("%", os.sep)
        endInputCoordinatesURL = self.dir + '%digiroad%test%data%geojson%reititinTestPoints.geojson'.replace("%", os.sep)
        outputFolderFeaturesURL = self.dir + '%digiroad%test%data%outputFolder%'.replace("%", os.sep)

        expectedJsonURL = self.dir + '%digiroad%test%data%geojson%manyToManyCostSummary.geojson'.replace("%", os.sep)

        expectedResult = self.fileActions.readJson(expectedJsonURL)

        self.metroAccessDigiroad.createMultiPointSummary(
            startCoordinatesGeojsonFilename=startInputCoordinatesURL,
            endCoordinatesGeojsonFilename=endInputCoordinatesURL,
            costAttribute=CostAttributes.DISTANCE,
            folderPath=outputFolderFeaturesURL,
            outputFilename="manyToManyCostSummary.geojson"
        )

        summaryOutputFolderFeaturesURL = outputFolderFeaturesURL + os.sep + "summary" + os.sep
        summaryResult = self.fileActions.readJson(
            summaryOutputFolderFeaturesURL + getEnglishMeaning(
                CostAttributes.DISTANCE) + "_manyToManyCostSummary.geojson")

        self.assertEqual(expectedResult, summaryResult)

    def readOutputFolderFiles(self, outputFeaturesURL):
        outputFileList = []
        for file in os.listdir(outputFeaturesURL):
            if file.endswith(".geojson"):
                outputFileList.append(file)

        return outputFileList
