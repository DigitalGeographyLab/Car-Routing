import os
# from src.digiroad.carRoutingExceptions import NotWFSDefinedException, NotURLDefinedException  # ONLY test purposes
import time

from digiroad.carRoutingExceptions import NotWFSDefinedException, NotURLDefinedException
from digiroad.entities import Point
from digiroad.logic.Operations import Operations
from digiroad.reflection import Reflection
from digiroad.util import CostAttributes, GeometryType, getEnglishMeaning, getFormattedDatetime, \
    timeDifference, FileActions


class MetropAccessDigiroadApplication:
    def __init__(self, wfsServiceProvider=None, postgisServiceProvider=None):
        self.fileActions = FileActions()
        self.operations = Operations(FileActions())
        self.reflection = Reflection()
        self.wfsServiceProvider = wfsServiceProvider
        self.postgisServiceProvider = postgisServiceProvider

    def calculateTotalTimeTravel(self,
                                 startCoordinatesGeojsonFilename=None,
                                 endCoordinatesGeojsonFilename=None,
                                 outputFolderPath=None,
                                 costAttribute=None):
        """
        Given a set of pair points and the ``cost attribute``, calculate the shortest path between each of them and
        store the Shortest Path Geojson file in the ``outputFolderPath``.

        :param wfsServiceProvider: WFS Service Provider data connection
        :param startCoordinatesGeojsonFilename: Geojson file (Geometry type: MultiPoint) containing pair of points.
        :param outputFolderPath: URL to store the shortest path geojson features of each pair of points.
        :param costAttribute: Attribute to calculate the impedance of the Shortest Path algorithm.
        :return: None. Store the information in the ``outputFolderPath``.
        """

        if not self.wfsServiceProvider:
            raise NotWFSDefinedException()
        if not startCoordinatesGeojsonFilename or not outputFolderPath:
            raise NotURLDefinedException()

        startTime = time.time()
        print("calculateTotalTimeTravel Start Time: %s" % getFormattedDatetime(timemilis=startTime))

        if isinstance(costAttribute, dict):
            for key in costAttribute:
                newOutputFolderPath = outputFolderPath + os.sep + "geoms" + os.sep + getEnglishMeaning(
                    costAttribute[key]) + os.sep
                self.fileActions.deleteFolder(path=newOutputFolderPath)
        else:
            newOutputFolderPath = outputFolderPath + os.sep + "geoms" + os.sep + getEnglishMeaning(
                costAttribute) + os.sep
            self.fileActions.deleteFolder(path=newOutputFolderPath)

        inputStartCoordinates = self.operations.mergeAdditionalLayers(
            originalJsonURL=startCoordinatesGeojsonFilename,
            outputFolderPath=outputFolderPath
        )

        inputEndCoordinates = self.operations.mergeAdditionalLayers(
            originalJsonURL=endCoordinatesGeojsonFilename,
            outputFolderPath=outputFolderPath
        )

        epsgCode = self.extractCRS(inputStartCoordinates)

        for startPointFeature in inputStartCoordinates["features"]:
            startCoordinates = startPointFeature["geometry"]["coordinates"]

            startPoint = Point(latitute=startCoordinates[1],
                               longitude=startCoordinates[0],
                               epsgCode=epsgCode)

            startPoint = self.operations.transformPoint(startPoint, self.wfsServiceProvider.getEPSGCode())
            startPointNearestVertexGeojson = self.wfsServiceProvider.getNearestCarRoutableVertexFromAPoint(
                startPoint)
            newFeatureStartPoint = startPointNearestVertexGeojson["features"][0]
            startNearestVertexCoordinates = newFeatureStartPoint["geometry"]["coordinates"][0]
            epsgCodeNearestVertexCoordinates = self.extractCRS(startPointNearestVertexGeojson)
            nearestStartPoint = Point(latitute=startNearestVertexCoordinates[1],
                                      longitude=startNearestVertexCoordinates[0],
                                      epsgCode=epsgCodeNearestVertexCoordinates)
            startVertexId = newFeatureStartPoint["id"].split(".")[1]

            ######## Add new properties to the start point feature
            startPointFeature["properties"]["selectedPointCoordinates"] = [startPoint.getLongitude(),
                                                                           startPoint.getLatitude()]
            startPointFeature["properties"]["nearestVertexCoordinates"] = [nearestStartPoint.getLongitude(),
                                                                           nearestStartPoint.getLatitude()]
            startPointFeature["properties"]["coordinatesCRS"] = startPoint.getEPSGCode()
            ########

            for endPointFeature in inputEndCoordinates["features"]:
                endCoordinates = endPointFeature["geometry"]["coordinates"]
                endPoint = Point(latitute=endCoordinates[1],
                                 longitude=endCoordinates[0],
                                 epsgCode=epsgCode)
                endPoint = self.operations.transformPoint(endPoint, self.wfsServiceProvider.getEPSGCode())

                if not startPoint.equals(endPoint):
                    endPointNearestVertexGeojson = self.wfsServiceProvider.getNearestCarRoutableVertexFromAPoint(
                        endPoint)

                    newFeatureEndPoint = endPointNearestVertexGeojson["features"][0]
                    endNearestVertexCoordinates = newFeatureEndPoint["geometry"]["coordinates"][0]
                    epsgCodeNearestVertexCoordinates = self.extractCRS(endPointNearestVertexGeojson)

                    nearestEndPoint = Point(latitute=endNearestVertexCoordinates[1],
                                            longitude=endNearestVertexCoordinates[0],
                                            epsgCode=epsgCodeNearestVertexCoordinates)
                    endVertexId = newFeatureEndPoint["id"].split(".")[1]

                    ######## Add new properties to the end point feature
                    endPointFeature["properties"]["selectedPointCoordinates"] = [endPoint.getLongitude(),
                                                                                 endPoint.getLatitude()]
                    endPointFeature["properties"]["nearestVertexCoordinates"] = [nearestEndPoint.getLongitude(),
                                                                                 nearestEndPoint.getLatitude()]
                    endPointFeature["properties"]["coordinatesCRS"] = startPoint.getEPSGCode()
                    ########

                    if isinstance(costAttribute, dict):
                        for key in costAttribute:
                            newOutputFolderPath = outputFolderPath + os.sep + "geoms" + os.sep + getEnglishMeaning(
                                costAttribute[key]) + os.sep
                            self.createShortestPathFileWithAdditionalProperties(costAttribute[key], startVertexId, endVertexId,
                                                                                startPoint, startPointFeature, endPoint,
                                                                                endPointFeature, nearestEndPoint,
                                                                                nearestStartPoint, newOutputFolderPath)
                    else:
                        self.createShortestPathFileWithAdditionalProperties(costAttribute, startVertexId, endVertexId,
                                                                            startPoint, startPointFeature, endPoint,
                                                                            endPointFeature, nearestEndPoint,
                                                                            nearestStartPoint, newOutputFolderPath)

        endTime = time.time()
        print("calculateTotalTimeTravel End Time: %s" % getFormattedDatetime(timemilis=endTime))

        totalTime = timeDifference(startTime, endTime)
        print("calculateTotalTimeTravel Total Time: %s m" % totalTime)

    def createShortestPathFileWithAdditionalProperties(self, costAttribute, startVertexId, endVertexId, startPoint,
                                                       startPointFeature, endPoint, endPointFeature, nearestEndPoint,
                                                       nearestStartPoint, outputFolderPath):
        shortestPath = self.wfsServiceProvider.getShortestPath(startVertexId=startVertexId,
                                                               endVertexId=endVertexId,
                                                               cost=costAttribute)
        shortestPath["overallProperties"] = {}
        additionalLayerOperationLinkedList = self.reflection.getLinkedAbstractAdditionalLayerOperation()
        while additionalLayerOperationLinkedList.hasNext():
            additionalLayerOperation = additionalLayerOperationLinkedList.next()

            newProperties = additionalLayerOperation.runOperation(
                featureJson=startPointFeature,
                prefix="startPoint_")
            for property in newProperties:
                startPointFeature["properties"][property] = newProperties[property]
                shortestPath["overallProperties"][property] = newProperties[property]

            newProperties = additionalLayerOperation.runOperation(
                featureJson=endPointFeature,
                prefix="endPoint_")
            for property in newProperties:
                endPointFeature["properties"][property] = newProperties[property]
                shortestPath["overallProperties"][property] = newProperties[property]

        shortestPath["overallProperties"]["selectedStartCoordinates"] = [startPoint.getLongitude(),
                                                                         startPoint.getLatitude()]
        shortestPath["overallProperties"]["selectedEndCoordinates"] = [endPoint.getLongitude(),
                                                                       endPoint.getLatitude()]
        shortestPath["overallProperties"]["nearestStartCoordinates"] = [nearestStartPoint.getLongitude(),
                                                                        nearestStartPoint.getLatitude()]
        shortestPath["overallProperties"]["nearestEndCoordinates"] = [nearestEndPoint.getLongitude(),
                                                                      nearestEndPoint.getLatitude()]

        filename = "shortestPath"
        extension = "geojson"
        completeFilename = "%s-%s-%s-%s.%s" % (
            filename, getEnglishMeaning(costAttribute), startVertexId, endVertexId, extension)
        self.fileActions.writeFile(folderPath=outputFolderPath, filename=completeFilename,
                                   data=shortestPath)

    def createSummary(self, folderPath, costAttribute, outputFilename):
        """
        Given a set of Geojson (Geometry type: LineString) files, read all the files from the given ``folderPath`` and
        sum all the attribute values (distance, speed_limit_time, day_avg_delay_time, midday_delay_time and
        rush_hour_delay_time) and create a simple features Geojson (Geometry type: LineString)
        with the summary information.

        :param folderPath: Folder containing the shortest path geojson features.
        :param outputFilename: Filename to give to the summary file.
        :return: None. Store the summary information in the folderPath with the name given in outputFilename.
        """
        startTime = time.time()
        print("createSummary Start Time: %s" % getFormattedDatetime(timemilis=startTime))

        if not folderPath.endswith(os.sep):
            attributeFolderPath = folderPath + os.sep + "geoms" + os.sep + getEnglishMeaning(costAttribute) + os.sep
            summaryFolderPath = folderPath + os.sep + "summary" + os.sep
        else:
            attributeFolderPath = folderPath + "geoms" + os.sep + getEnglishMeaning(costAttribute) + os.sep
            summaryFolderPath = folderPath + "summary" + os.sep

        totals = {
            "features": [],
            "totalFeatures": 0,
            "type": "FeatureCollection"
        }
        for file in os.listdir(attributeFolderPath):
            if file.endswith(".geojson") and file != "metroAccessDigiroadSummary.geojson":

                filemetadata = file.split("-")
                if len(filemetadata) < 2:
                    print(filemetadata)

                shortestPath = self.fileActions.readJson(url=attributeFolderPath + file)

                if "crs" not in totals:
                    totals["crs"] = shortestPath["crs"]

                newSummaryFeature = {
                    "geometry": {
                        "coordinates": [
                        ],
                        "type": GeometryType.LINE_STRING
                    },
                    "properties": {
                        "startVertexId": int(filemetadata[2]),
                        "endVertexId": int(filemetadata[3].replace(".geojson", "")),
                        "costAttribute": filemetadata[1]
                    }
                }

                for property in shortestPath["overallProperties"]:
                    newSummaryFeature["properties"][property] = shortestPath["overallProperties"][property]

                startPoints = None
                endPoints = None
                lastSequence = 1

                for segmentFeature in shortestPath["features"]:
                    for key in segmentFeature["properties"]:
                        if key == "seq":
                            if segmentFeature["properties"][key] == 1:
                                # Sequence one is the first linestring geometry in the path
                                startPoints = segmentFeature["geometry"]["coordinates"]
                            if segmentFeature["properties"][key] > lastSequence:
                                # The last sequence is the last linestring geometry in the path
                                endPoints = segmentFeature["geometry"]["coordinates"]
                                lastSequence = segmentFeature["properties"][key]

                        if key not in ["id", "direction", "seq"]:
                            if key not in newSummaryFeature["properties"]:
                                newSummaryFeature["properties"][key] = 0

                            newSummaryFeature["properties"][key] = newSummaryFeature["properties"][key] + \
                                                                   segmentFeature["properties"][key]

                try:
                    newSummaryFeature["geometry"]["coordinates"] = newSummaryFeature["geometry"]["coordinates"] + \
                                                                   startPoints

                    startAndEndPointAreDifferent = lastSequence > 1
                    if startAndEndPointAreDifferent:
                        newSummaryFeature["geometry"]["coordinates"] = newSummaryFeature["geometry"]["coordinates"] + \
                                                                       endPoints
                    totals["features"].append(newSummaryFeature)
                except Exception as err:
                    print(err)

        totals["totalFeatures"] = len(totals["features"])
        outputFilename = getEnglishMeaning(costAttribute) + "_" + outputFilename
        self.fileActions.writeFile(folderPath=summaryFolderPath, filename=outputFilename, data=totals)

        endTime = time.time()
        print("createSummary End Time: %s" % getFormattedDatetime(timemilis=endTime))

        totalTime = timeDifference(startTime, endTime)
        print("createSummary Total Time: %s m" % totalTime)

    def createMultiPointSummary(self, startCoordinatesGeojsonFilename, endCoordinatesGeojsonFilename, costAttribute,
                                folderPath, outputFilename):
        """
        Using the power of pgr_Dijsktra algorithm this function calculate the total routing cost for a pair of set of points.
        It differentiate if must to use one-to-one, one-to-many, many-to-one or many-to-many specific stored procedures from the pgrouting extension.

        :param startCoordinatesGeojsonFilename: Geojson file (Geometry type: MultiPoint) containing pair of points.
        :param outputFolderPath: URL to store the shortest path geojson features of each pair of points.
        :param costAttribute: Attribute to calculate the impedance of the Shortest Path algorithm.
        :param folderPath: Folder containing the shortest path geojson features.
        :param outputFilename: Filename to give to the summary file.
        :return: None. Store the information in the ``outputFolderPath``.
        """

        startTime = time.time()
        print("createMultiPointSummary Start Time: %s" % getFormattedDatetime(timemilis=startTime))

        startCoordinatesJson = self.fileActions.readJson(url=startCoordinatesGeojsonFilename)
        endCoordinatesJson = self.fileActions.readJson(url=endCoordinatesGeojsonFilename)

        startVertexesID = self.getVertexesID(startCoordinatesJson)
        endVertexesID = self.getVertexesID(endCoordinatesJson)

        totals = None

        if len(startVertexesID) == 1 and len(endVertexesID) == 1:
            totals = self.postgisServiceProvider.getTotalShortestPathCostOneToOne(
                startVertexID=startVertexesID[0],
                endVertexID=endVertexesID[0],
                costAttribute=costAttribute
            )
        elif len(startVertexesID) == 1 and len(endVertexesID) > 1:
            totals = self.postgisServiceProvider.getTotalShortestPathCostOneToMany(
                startVertexID=startVertexesID[0],
                endVertexesID=endVertexesID,
                costAttribute=costAttribute
            )
        elif len(startVertexesID) > 1 and len(endVertexesID) == 1:
            totals = self.postgisServiceProvider.getTotalShortestPathCostManyToOne(
                startVertexesID=startVertexesID,
                endVertexID=endVertexesID[0],
                costAttribute=costAttribute
            )
        elif len(startVertexesID) > 1 and len(endVertexesID) > 1:
            totals = self.postgisServiceProvider.getTotalShortestPathCostManyToMany(
                startVertexesID=startVertexesID,
                endVertexesID=endVertexesID,
                costAttribute=costAttribute
            )

        if not folderPath.endswith(os.sep):
            summaryFolderPath = folderPath + os.sep + "summary" + os.sep
        else:
            summaryFolderPath = folderPath + "summary" + os.sep

        outputFilename = getEnglishMeaning(costAttribute) + "_" + outputFilename
        self.fileActions.writeFile(folderPath=summaryFolderPath, filename=outputFilename, data=totals)

        endTime = time.time()
        print("createMultiPointSummary End Time: %s" % getFormattedDatetime(timemilis=endTime))

        totalTime = timeDifference(startTime, endTime)
        print("createMultiPointSummary Total Time: %s m" % totalTime)

    def extractCRS(self, geojson):
        epsgCode = geojson["crs"]["properties"]["name"].split(":")[-3] + ":" + \
                   geojson["crs"]["properties"]["name"].split(":")[-1]
        return epsgCode

    def getVertexesID(self, geojson):
        endEPSGCode = self.extractCRS(geojson)
        vertexesID = []

        for feature in geojson["features"]:
            coordinates = feature["geometry"]["coordinates"]

            featurePoint = Point(latitute=coordinates[1],
                                 longitude=coordinates[0],
                                 epsgCode=endEPSGCode)

            featurePoint = self.operations.transformPoint(featurePoint, self.wfsServiceProvider.getEPSGCode())
            nearestVertexGeojson = self.wfsServiceProvider.getNearestCarRoutableVertexFromAPoint(
                featurePoint)
            newFeaturePoint = nearestVertexGeojson["features"][0]
            vertexesID.append(newFeaturePoint["id"].split(".")[1])

        return vertexesID
