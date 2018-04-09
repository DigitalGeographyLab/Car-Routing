import os
import unittest

import time

import multiprocessing
from joblib import Parallel, delayed
from math import sqrt

from digiroad.carRoutingExceptions import WFSNotDefinedException, NotURLDefinedException, \
    TransportModeNotDefinedException
from digiroad.connection.PostgisServiceProvider import PostgisServiceProvider
from digiroad.logic.MetropAccessDigiroad import MetropAccessDigiroadApplication
from digiroad.transportMode.PrivateCarTransportMode import PrivateCarTransportMode
from digiroad.util import CostAttributes, getEnglishMeaning, FileActions


class MetropAccessDigiroadTest(unittest.TestCase):
    def setUp(self):
        # self.wfsServiceProvider = WFSServiceProvider(wfs_url="http://localhost:8080/geoserver/wfs?",
        #                                              nearestVertexTypeName="tutorial:dgl_nearest_vertex",
        #                                              nearestCarRoutingVertexTypeName="tutorial:dgl_nearest_car_routable_vertex",
        #                                              shortestPathTypeName="tutorial:dgl_shortest_path",
        #                                              outputFormat="application/json")
        self.postgisServiceProvider = PostgisServiceProvider()
        self.transportMode = PrivateCarTransportMode(self.postgisServiceProvider)
        self.metroAccessDigiroad = MetropAccessDigiroadApplication(self.transportMode)
        self.fileActions = FileActions()
        self.dir = os.getcwd()

    def test_givenNoneWFSService_Then_ThrowError(self):
        metroAccessDigiroad = MetropAccessDigiroadApplication(None)
        self.assertRaises(TransportModeNotDefinedException, metroAccessDigiroad.calculateTotalTimeTravel, "", "", "", "")

    def test_givenEmtpyURL_Then_ThrowError(self):
        inputCoordinatesURL = None
        outputFolderFeaturesURL = None
        testPolygonsURL = None

        self.assertRaises(NotURLDefinedException,
                          self.metroAccessDigiroad.calculateTotalTimeTravel,
                          inputCoordinatesURL,
                          inputCoordinatesURL,
                          outputFolderFeaturesURL,
                          testPolygonsURL)

    def test_givenAPointGeojson_then_returnGeojsonFeatures(self):
        inputCoordinatesURL = self.dir + '%digiroad%test%data%geojson%onePoint.geojson'.replace("%", os.sep)
        input2CoordinatesURL = self.dir + '%digiroad%test%data%geojson%anotherPoint.geojson'.replace("%", os.sep)
        outputFolderFeaturesURL = self.dir + '%digiroad%test%data%outputFolderTemp%'.replace("%", os.sep)
        expectedResultPath = self.dir + '%digiroad%test%data%geojson%shortpathBetweenTwoPoints.geojson'.replace("%",
                                                                                                                os.sep)

        # distanceCostAttribute = CostAttributes.DISTANCE
        distanceCostAttribute = {
            "DISTANCE": CostAttributes.DISTANCE
            # "SPEED_LIMIT_TIME": CostAttributes.SPEED_LIMIT_TIME,
            # "DAY_AVG_DELAY_TIME": CostAttributes.DAY_AVG_DELAY_TIME,
            # "MIDDAY_DELAY_TIME": CostAttributes.MIDDAY_DELAY_TIME,
            # "RUSH_HOUR_DELAY": CostAttributes.RUSH_HOUR_DELAY
        }
        self.metroAccessDigiroad.calculateTotalTimeTravel(startCoordinatesGeojsonFilename=inputCoordinatesURL,
                                                          endCoordinatesGeojsonFilename=input2CoordinatesURL,
                                                          outputFolderPath=outputFolderFeaturesURL,
                                                          costAttribute=distanceCostAttribute)

        inputCoordinatesGeojson = self.fileActions.readJson(inputCoordinatesURL)
        expectedResult = self.fileActions.readJson(expectedResultPath)

        if not outputFolderFeaturesURL.endswith(os.sep):
            geomsOutputFolderFeaturesURL = outputFolderFeaturesURL + os.sep + \
                                           "geoms" + os.sep + \
                                           getEnglishMeaning(CostAttributes.DISTANCE) + os.sep
        else:
            geomsOutputFolderFeaturesURL = outputFolderFeaturesURL + "geoms" + os.sep + getEnglishMeaning(
                CostAttributes.DISTANCE) + os.sep

        outputFileList = self.readOutputFolderFiles(geomsOutputFolderFeaturesURL)

        outputFilename = outputFileList[0]
        outputFilePath = outputFolderFeaturesURL + os.sep + "geoms" + os.sep + getEnglishMeaning(
            CostAttributes.DISTANCE) + os.sep + outputFilename

        outputResult = self.fileActions.readJson(outputFilePath)

        for feature in expectedResult["features"]:
            if "id" in feature:
                del feature["id"]

        maxSeq = 0
        for feature in outputResult["features"]:
            maxSeq = max(feature["properties"]["seq"], maxSeq)
            if "id" in feature:
                del feature["id"]

        self.assertEqual(expectedResult, outputResult)

    @unittest.skip("")  # about 13 m for 12 points (132 possible paths)
    def test_givenAMultiPointGeojson_then_returnGeojsonFeatures(self):
        inputStartCoordinatesURL = self.dir + '%digiroad%test%data%geojson%reititinTestPoints.geojson'.replace("%", os.sep)
        inputEndCoordinatesURL = self.dir + '%digiroad%test%data%geojson%reititinTestPoints.geojson'.replace("%", os.sep)
        # inputStartCoordinatesURL = self.dir + '%digiroad%test%data%geojson%not-fast-points.geojson'.replace("%", os.sep)
        # inputEndCoordinatesURL = self.dir + '%digiroad%test%data%geojson%not-fast-points2.geojson'.replace("%", os.sep)
        # outputFolderFeaturesURL = self.dir + '%digiroad%test%data%outputFolderNotFast3%'.replace("%", os.sep)
        outputFolderFeaturesURL = self.dir + '%digiroad%test%data%outputFolder%'.replace("%", os.sep)

        distanceCostAttribute = CostAttributes.DISTANCE
        # distanceCostAttribute = {
        #     "DISTANCE": CostAttributes.DISTANCE,
        #     "SPEED_LIMIT_TIME": CostAttributes.SPEED_LIMIT_TIME,
        #     "DAY_AVG_DELAY_TIME": CostAttributes.DAY_AVG_DELAY_TIME,
        #     "MIDDAY_DELAY_TIME": CostAttributes.MIDDAY_DELAY_TIME,
        #     "RUSH_HOUR_DELAY": CostAttributes.RUSH_HOUR_DELAY
        # }
        self.metroAccessDigiroad.calculateTotalTimeTravel(startCoordinatesGeojsonFilename=inputStartCoordinatesURL,
                                                          endCoordinatesGeojsonFilename=inputEndCoordinatesURL,
                                                          outputFolderPath=outputFolderFeaturesURL,
                                                          costAttribute=distanceCostAttribute)

        inputCoordinatesGeojson = self.fileActions.readJson(inputStartCoordinatesURL)
        for key in distanceCostAttribute:
            if not outputFolderFeaturesURL.endswith(os.sep):
                geomsOutputFolderFeaturesURL = outputFolderFeaturesURL + os.sep + \
                                               "geoms" + os.sep + getEnglishMeaning(distanceCostAttribute[key]) + os.sep
            else:
                geomsOutputFolderFeaturesURL = outputFolderFeaturesURL + "geoms" + os.sep + getEnglishMeaning(
                    distanceCostAttribute[key]) + os.sep

            outputFileList = self.readOutputFolderFiles(geomsOutputFolderFeaturesURL)

            totalCombinatory = len(inputCoordinatesGeojson["features"]) * len(
                inputCoordinatesGeojson["features"]) - len(
                inputCoordinatesGeojson["features"])
            self.assertEqual(totalCombinatory, len(outputFileList))

    def test_givenAListOfGeojson_then_createSummary(self):
        self.maxDiff = None
        expectedJsonURL = self.dir + '%digiroad%test%data%geojson%metroAccessDigiroadSummaryResult.geojson'.replace("%",
                                                                                                                    os.sep)
        outputFolderFeaturesURL = self.dir + '%digiroad%test%data%outputFolder%'.replace("%", os.sep)

        expectedResult = self.fileActions.readJson(expectedJsonURL)
        self.metroAccessDigiroad.createDetailedSummary(outputFolderFeaturesURL,
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

        expectedJsonURL = self.dir + '%digiroad%test%data%geojson%oneToOneCostSummaryAdditionalInfo.geojson'.replace(
            "%", os.sep)

        expectedResult = self.fileActions.readJson(expectedJsonURL)

        self.metroAccessDigiroad.createGeneralSummary(
            startCoordinatesGeojsonFilename=startInputCoordinatesURL,
            endCoordinatesGeojsonFilename=endInputCoordinatesURL,
            costAttribute=CostAttributes.DISTANCE,
            outputFolderPath=outputFolderFeaturesURL,
            outputFilename="oneToOneCostSummary.geojson"
        )

        summaryOutputFolderFeaturesURL = outputFolderFeaturesURL + os.sep + "summary" + os.sep
        summaryResult = self.fileActions.readJson(
            summaryOutputFolderFeaturesURL + getEnglishMeaning(
                CostAttributes.DISTANCE) + "_oneToOneCostSummary.geojson")

        self.assertEqual(expectedResult, summaryResult)

    def test_givenOneStartPointGeojsonAndManyEndPointsGeojson_then_createMultiPointSummary(self):
        startInputCoordinatesURL = self.dir + '%digiroad%test%data%geojson%onePoint.geojson'.replace("%", os.sep)
        endInputCoordinatesURL = self.dir + '%digiroad%test%data%geojson%reititinTestPoints.geojson'.replace("%",
                                                                                                             os.sep)
        outputFolderFeaturesURL = self.dir + '%digiroad%test%data%outputFolder%'.replace("%", os.sep)

        expectedJsonURL = self.dir + '%digiroad%test%data%geojson%oneToManyCostSummaryAdditionalInfo.geojson'.replace(
            "%", os.sep)

        expectedResult = self.fileActions.readJson(expectedJsonURL)

        self.metroAccessDigiroad.createGeneralSummary(
            startCoordinatesGeojsonFilename=startInputCoordinatesURL,
            endCoordinatesGeojsonFilename=endInputCoordinatesURL,
            costAttribute=CostAttributes.DISTANCE,
            outputFolderPath=outputFolderFeaturesURL,
            outputFilename="oneToManyCostSummary.geojson"
        )

        summaryOutputFolderFeaturesURL = outputFolderFeaturesURL + os.sep + "summary" + os.sep
        summaryResult = self.fileActions.readJson(
            summaryOutputFolderFeaturesURL + getEnglishMeaning(
                CostAttributes.DISTANCE) + "_oneToManyCostSummary.geojson")

        self.assertEqual(expectedResult, summaryResult)

    def test_givenManyStartPointsGeojsonAndOneEndPointGeojson_then_createMultiPointSummary(self):
        startInputCoordinatesURL = self.dir + '%digiroad%test%data%geojson%reititinTestPoints.geojson'.replace("%",
                                                                                                               os.sep)
        endInputCoordinatesURL = self.dir + '%digiroad%test%data%geojson%onePoint.geojson'.replace("%", os.sep)
        outputFolderFeaturesURL = self.dir + '%digiroad%test%data%outputFolder%'.replace("%", os.sep)

        expectedJsonURL = self.dir + '%digiroad%test%data%geojson%manyToOneCostSummaryAdditionalInfo.geojson'.replace(
            "%", os.sep)

        expectedResult = self.fileActions.readJson(expectedJsonURL)

        self.metroAccessDigiroad.createGeneralSummary(
            startCoordinatesGeojsonFilename=startInputCoordinatesURL,
            endCoordinatesGeojsonFilename=endInputCoordinatesURL,
            costAttribute=CostAttributes.DISTANCE,
            outputFolderPath=outputFolderFeaturesURL,
            outputFilename="manyToOneCostSummary.geojson"
        )

        summaryOutputFolderFeaturesURL = outputFolderFeaturesURL + os.sep + "summary" + os.sep
        summaryResult = self.fileActions.readJson(
            summaryOutputFolderFeaturesURL + getEnglishMeaning(
                CostAttributes.DISTANCE) + "_manyToOneCostSummary.geojson")

        self.assertEqual(expectedResult, summaryResult)

    def test_givenManyStartPointsGeojsonAndManyEndPointsGeojson_then_createMultiPointSummary(self):
        # startInputCoordinatesURL = self.dir + '%digiroad%test%data%geojson%pointsInTheForest.geojson'.replace("%", os.sep)
        # endInputCoordinatesURL = self.dir + '%digiroad%test%data%geojson%rautatientoriPoint.geojson'.replace("%", os.sep)

        startInputCoordinatesURL = self.dir + '%digiroad%test%data%geojson%reititinTestPoints.geojson'.replace("%",
                                                                                                               os.sep)
        endInputCoordinatesURL = self.dir + '%digiroad%test%data%geojson%reititinTestPoints.geojson'.replace("%",
                                                                                                             os.sep)
        outputFolderFeaturesURL = self.dir + '%digiroad%test%data%outputFolderForest%'.replace("%", os.sep)

        expectedJsonURL = self.dir + '%digiroad%test%data%geojson%manyToManyCostSummaryAdditionalInfo.geojson'.replace(
            "%", os.sep)

        expectedResult = self.fileActions.readJson(expectedJsonURL)

        self.metroAccessDigiroad.createGeneralSummary(
            startCoordinatesGeojsonFilename=startInputCoordinatesURL,
            endCoordinatesGeojsonFilename=endInputCoordinatesURL,
            costAttribute=CostAttributes.DISTANCE,
            outputFolderPath=outputFolderFeaturesURL,
            outputFilename="manyToManyCostSummary.geojson"
        )

        summaryOutputFolderFeaturesURL = outputFolderFeaturesURL + os.sep + "summary" + os.sep
        summaryResult = self.fileActions.readJson(
            summaryOutputFolderFeaturesURL + getEnglishMeaning(
                CostAttributes.DISTANCE) + "_manyToManyCostSummary.geojson")

        self.assertEqual(expectedResult, summaryResult)

    ################################################
    @unittest.SkipTest
    def test_givenYKRGridCellPoints_then_createMultiPointSummary(self):
        startInputCoordinatesURL = self.dir + '%digiroad%test%data%geojson%sampleYKRGridPoints-13000.geojson'.replace(
            "%",
            os.sep)
        endInputCoordinatesURL = self.dir + '%digiroad%test%data%geojson%sampleYKRGridPoints-5.geojson'.replace("%",
                                                                                                                    os.sep)
        outputFolderFeaturesURL = self.dir + '%digiroad%test%data%outputFolderYKR-13000-5-newRoadNetwork%'.replace("%", os.sep)

        # startInputCoordinatesURL = self.dir + '%digiroad%test%data%geojson%sampleYKRGridPoints-100.geojson'.replace("%",
        #                                                                                                           os.sep)
        # endInputCoordinatesURL = self.dir + '%digiroad%test%data%geojson%sampleYKRGridPoints-100.geojson'.replace("%",
        #                                                                                                             os.sep)
        # outputFolderFeaturesURL = self.dir + '%digiroad%test%data%outputFolderYKR-100%'.replace("%", os.sep)

        # expectedJsonURL = self.dir + '%digiroad%test%data%geojson%oneToOneCostSummaryAdditionalInfo.geojson'.replace("%", os.sep)

        # expectedResult = self.fileActions.readJson(expectedJsonURL)

        self.metroAccessDigiroad.createGeneralSummary(
            startCoordinatesGeojsonFilename=startInputCoordinatesURL,
            endCoordinatesGeojsonFilename=endInputCoordinatesURL,
            costAttribute=CostAttributes.RUSH_HOUR_DELAY,
            outputFolderPath=outputFolderFeaturesURL,
            outputFilename="YKRCostSummary-13000-5.geojson"
        )

        summaryOutputFolderFeaturesURL = outputFolderFeaturesURL + os.sep + "summary" + os.sep
        summaryResult = self.fileActions.readJson(
            summaryOutputFolderFeaturesURL + getEnglishMeaning(
                CostAttributes.RUSH_HOUR_DELAY) + "_YKRCostSummary-13000-5.geojson")

        # self.assertEqual(expectedResult, summaryResult)
        self.assertIsNotNone(summaryResult)

    def readOutputFolderFiles(self, outputFeaturesURL):
        outputFileList = []
        for file in os.listdir(outputFeaturesURL):
            if file.endswith(".geojson"):
                outputFileList.append(file)

        return outputFileList

    def test_parallelism(self):
        with Parallel(n_jobs=2, backend="threading", verbose=5) as parallel:
            accumulator = 0.
            n_iter = 0
            while accumulator < 1000:
                results = parallel(delayed(myDelay)(accumulator + i ** 2) for i in range(5))
                accumulator += sum(results)  # synchronization barrier
                n_iter += 1
        print(accumulator, n_iter)

    @unittest.SkipTest
    def test_parallelism2(self):
        vertexIDs = multiprocessing.Queue()
        features = multiprocessing.Queue()
        # Setup a list of processes that we want to run
        pool = multiprocessing.Pool(processes=4)
        processes = [pool.apply_async(func=mySubprocess, args=(vertexIDs, features, x)) for x in range(4)]

        # # Run processes
        # for p in processes:
        #     p.start()
        #
        # # Exit the completed processes
        # for p in processes:
        #     p.join()

        # Get process results from the output queue
        # results = [output.get() for p in processes]
        self.assertRaises(RuntimeError, [p.get() for p in processes])
        # Queue objects should only be shared between processes through inheritance


def mySubprocess(vertexIDs, features, item):
    vertexIDs.put(item)
    features.put(str(item))
    return vertexIDs, features


def myDelay(number):
    # time.sleep(1)
    return sqrt(number)
