import copy
import os

from joblib import delayed, Parallel

from digiroad.carRoutingExceptions import NotURLDefinedException, \
    TransportModeNotDefinedException
from digiroad.entities import Point
from digiroad.logic.Operations import Operations
from digiroad.reflection import Reflection
from digiroad.util import GeometryType, getEnglishMeaning, FileActions, extractCRS, createPointFromPointFeature, \
    getConfigurationProperties, dgl_timer_enabled, \
    dgl_timer, parallel_job_print, Logger


# from src.digiroad.carRoutingExceptions import NotWFSDefinedException, NotURLDefinedException  # ONLY test purposes


def extractFeatureInformation(self, endEPSGCode, feature, geojsonServiceProvider, operations):
    pointIdentifierKey = getConfigurationProperties(section="WFS_CONFIG")["point_identifier"]

    pointId = feature["properties"][pointIdentifierKey]
    if pointId in self.nearestVerticesCache:
        return self.nearestVerticesCache[pointId]

    coordinates = feature["geometry"]["coordinates"]
    featurePoint = Point(latitute=coordinates[1],
                         longitude=coordinates[0],
                         epsgCode=endEPSGCode)
    featurePoint = operations.transformPoint(featurePoint, geojsonServiceProvider.getEPSGCode())
    nearestVertexGeojson = geojsonServiceProvider.getNearestRoutableVertexFromAPoint(
        featurePoint)
    newFeaturePoint = nearestVertexGeojson["features"][0]
    vertexID = newFeaturePoint["properties"]["id"]
    feature["properties"]["vertex_id"] = vertexID
    ###
    epsgCodeNearestVertexCoordinates = extractCRS(nearestVertexGeojson)
    nearestPoint = createPointFromPointFeature(newFeaturePoint, epsgCodeNearestVertexCoordinates)
    nearestPoint = operations.transformPoint(nearestPoint, geojsonServiceProvider.getEPSGCode())
    ######## Add new properties to the start point feature
    feature["properties"]["selectedPointCoordinates"] = [featurePoint.getLongitude(),
                                                         featurePoint.getLatitude()]
    feature["properties"]["nearestVertexCoordinates"] = [nearestPoint.getLongitude(),
                                                         nearestPoint.getLatitude()]
    feature["properties"]["coordinatesCRS"] = featurePoint.getEPSGCode()
    ###

    self.nearestVerticesCache[pointId] = (vertexID, feature)

    return vertexID, feature


def createCostSummaryWithAdditionalProperties(self, costAttribute, startPointFeature, endPointFeature,
                                              costSummaryMap):
    startVertexID = startPointFeature["properties"]["vertex_id"]
    endVertexID = endPointFeature["properties"]["vertex_id"]

    # if startVertexID == endVertexID:
    #     return None
    if (startVertexID not in costSummaryMap) or (endVertexID not in costSummaryMap[startVertexID]):
        Logger.getInstance().warning("Not contained into the costSummaryMap: %s %s" % (startVertexID, endVertexID))
        return None

    summaryFeature = costSummaryMap[startVertexID][endVertexID]
    summaryFeature = copy.deepcopy(summaryFeature)

    total_cost = summaryFeature["properties"]["total_cost"]

    del summaryFeature["properties"]["start_vertex_id"]
    del summaryFeature["properties"]["end_vertex_id"]
    del summaryFeature["properties"]["total_cost"]

    # pointIdentifierKey = getConfigurationProperties(section="WFS_CONFIG")["point_identifier"]

    # startPointId = startPointFeature["properties"][pointIdentifierKey]
    # endPointId = endPointFeature["properties"][pointIdentifierKey]

    # newPropertiesId = startPointId + "-" + endPointId
    # if newPropertiesId in self.additionalFeaturePropertiesCache:
    #     newProperties = self.additionalFeaturePropertiesCache[newPropertiesId]
    # else:
    newProperties = self.insertAdditionalProperties(
        startPointFeature,
        endPointFeature
    )
    # self.additionalFeaturePropertiesCache[newPropertiesId] = newProperties

    # coordinates = summaryFeature["geometry"]["coordinates"]
    # coordinates[0] = startPointFeature["properties"]["selectedPointCoordinates"]
    # coordinates[1] = endPointFeature["properties"]["selectedPointCoordinates"]

    newProperties["costAttribute"] = getEnglishMeaning(costAttribute)
    newProperties[getEnglishMeaning(costAttribute)] = total_cost
    newProperties["startVertexId"] = startVertexID
    newProperties["endVertexId"] = endVertexID
    newProperties["selectedStartCoordinates"] = startPointFeature["properties"]["selectedPointCoordinates"]
    newProperties["selectedEndCoordinates"] = endPointFeature["properties"]["selectedPointCoordinates"]
    newProperties["nearestStartCoordinates"] = startPointFeature["properties"]["nearestVertexCoordinates"]
    newProperties["nearestEndCoordinates"] = endPointFeature["properties"]["nearestVertexCoordinates"]
    for key in newProperties:
        summaryFeature["properties"][key] = newProperties[key]

    return summaryFeature


class MetropAccessDigiroadApplication:
    def __init__(self, transportMode=None):
        self.fileActions = FileActions()
        self.operations = Operations(FileActions())
        self.reflection = Reflection()
        self.transportMode = transportMode
        self.nearestVerticesCache = {}
        self.additionalStartFeaturePropertiesCache = {}
        self.additionalEndFeaturePropertiesCache = {}

    @dgl_timer_enabled
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

        if not self.transportMode:
            raise TransportModeNotDefinedException()
        if not startCoordinatesGeojsonFilename or not outputFolderPath:
            raise NotURLDefinedException()

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

        epsgCode = self.operations.extractCRSWithGeopandas(
            startCoordinatesGeojsonFilename)  # extractCRS(inputStartCoordinates)

        for startPointFeature in inputStartCoordinates["features"]:
            startCoordinates = startPointFeature["geometry"]["coordinates"]

            startPoint = Point(latitute=startCoordinates[1],
                               longitude=startCoordinates[0],
                               epsgCode=epsgCode)

            startPoint = self.operations.transformPoint(startPoint, self.transportMode.getEPSGCode())
            startPointNearestVertexGeojson = self.transportMode.getNearestRoutableVertexFromAPoint(
                startPoint)
            newFeatureStartPoint = startPointNearestVertexGeojson["features"][0]
            startPointEPSGCode = self.operations.extractCRSWithGeopandas(
                startCoordinatesGeojsonFilename)  # extractCRS(startPointNearestVertexGeojson)
            nearestStartPoint = createPointFromPointFeature(newFeatureStartPoint, startPointEPSGCode)
            startVertexId = newFeatureStartPoint["properties"]["id"]

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
                endPoint = self.operations.transformPoint(endPoint, self.transportMode.getEPSGCode())

                if not startPoint.equals(endPoint):
                    endPointNearestVertexGeojson = self.transportMode.getNearestRoutableVertexFromAPoint(
                        endPoint)

                    newFeatureEndPoint = endPointNearestVertexGeojson["features"][0]
                    # endPointEPSGCode = extractCRS(endPointNearestVertexGeojson)
                    nearestEndPoint = createPointFromPointFeature(newFeatureEndPoint,
                                                                  startPointEPSGCode  # endPointEPSGCode
                                                                  )
                    endVertexId = newFeatureEndPoint["properties"]["id"]

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
                            self.createShortestPathFileWithAdditionalProperties(costAttribute[key], startVertexId,
                                                                                endVertexId,
                                                                                startPoint, startPointFeature, endPoint,
                                                                                endPointFeature, nearestEndPoint,
                                                                                nearestStartPoint, newOutputFolderPath)
                    else:
                        self.createShortestPathFileWithAdditionalProperties(costAttribute, startVertexId, endVertexId,
                                                                            startPoint, startPointFeature, endPoint,
                                                                            endPointFeature, nearestEndPoint,
                                                                            nearestStartPoint, newOutputFolderPath)
    @dgl_timer
    def createShortestPathFileWithAdditionalProperties(self, costAttribute, startVertexId, endVertexId, startPoint,
                                                       startPointFeature, endPoint, endPointFeature, nearestEndPoint,
                                                       nearestStartPoint, outputFolderPath):
        shortestPath = self.transportMode.getShortestPath(startVertexId=startVertexId,
                                                          endVertexId=endVertexId,
                                                          cost=costAttribute)
        shortestPath["overallProperties"] = self.insertAdditionalProperties(
            startPointFeature,
            endPointFeature
        )

        shortestPath["overallProperties"]["selectedStartCoordinates"] = [startPoint.getLongitude(),
                                                                         startPoint.getLatitude()]
        shortestPath["overallProperties"]["selectedEndCoordinates"] = [endPoint.getLongitude(),
                                                                       endPoint.getLatitude()]
        shortestPath["overallProperties"]["nearestStartCoordinates"] = [nearestStartPoint.getLongitude(),
                                                                        nearestStartPoint.getLatitude()]
        shortestPath["overallProperties"]["nearestEndCoordinates"] = [nearestEndPoint.getLongitude(),
                                                                      nearestEndPoint.getLatitude()]

        if "totalFeatures" not in shortestPath:
            shortestPath["totalFeatures"] = len(shortestPath["features"])

        filename = "shortestPath"
        extension = "geojson"
        completeFilename = "%s-%s-%s-%s.%s" % (
            filename, getEnglishMeaning(costAttribute), startVertexId, endVertexId, extension)
        self.fileActions.writeFile(folderPath=outputFolderPath, filename=completeFilename,
                                   data=shortestPath)

    def insertAdditionalProperties(self, startPointFeature, endPointFeature):
        startFeatureProperties = {}
        endFeatureProperties = {}

        pointIdentifierKey = getConfigurationProperties(section="WFS_CONFIG")["point_identifier"]

        startPointId = startPointFeature["properties"][pointIdentifierKey]
        endPointId = endPointFeature["properties"][pointIdentifierKey]

        existStartFeaturePropertiesCache = startPointId in self.additionalStartFeaturePropertiesCache
        if existStartFeaturePropertiesCache:
            startFeatureProperties = self.additionalStartFeaturePropertiesCache[startPointId]

        existEndFeaturePropertiesCache = endPointId in self.additionalEndFeaturePropertiesCache
        if existEndFeaturePropertiesCache:
            endFeatureProperties = self.additionalEndFeaturePropertiesCache[endPointId]


            # self.additionalFeaturePropertiesCache[newPropertiesId] = newProperties
        if (not existStartFeaturePropertiesCache) or (not existEndFeaturePropertiesCache):
            additionalLayerOperationLinkedList = self.reflection.getLinkedAbstractAdditionalLayerOperation()
            while additionalLayerOperationLinkedList.hasNext():
                additionalLayerOperation = additionalLayerOperationLinkedList.next()

                if not existStartFeaturePropertiesCache:
                    newPropertiesStartPointFeature = additionalLayerOperation.runOperation(
                        featureJson=startPointFeature,
                        prefix="startPoint_")
                    # for property in newPropertiesStartPointFeature:
                    #     startPointFeature["properties"][property] = newPropertiesStartPointFeature[property]
                    #     featureProperties[property] = newPropertiesStartPointFeature[property]
                    startFeatureProperties.update(newPropertiesStartPointFeature)

                if not existEndFeaturePropertiesCache:
                    newPropertiesEndPointFeature = additionalLayerOperation.runOperation(
                        featureJson=endPointFeature,
                        prefix="endPoint_")
                    # for property in newPropertiesEndPointFeature:
                    #     endPointFeature["properties"][property] = newPropertiesEndPointFeature[property]
                    #     featureProperties[property] = newPropertiesEndPointFeature[property]
                    endFeatureProperties.update(newPropertiesEndPointFeature)

        if not existStartFeaturePropertiesCache:
            self.additionalStartFeaturePropertiesCache[startPointId] = copy.deepcopy(startFeatureProperties)

        if not existEndFeaturePropertiesCache:
            self.additionalEndFeaturePropertiesCache[endPointId] = copy.deepcopy(endFeatureProperties)

        # featureProperties = {}
        # if existStartFeaturePropertiesCache:
        #     startFeatureProperties.update(endFeatureProperties)
        #     featureProperties = startFeatureProperties
        # elif existEndFeaturePropertiesCache:
        #     endFeatureProperties.update(startFeatureProperties)
        #     featureProperties = endFeatureProperties
        # else:
        startFeatureProperties.update(endFeatureProperties)
        featureProperties = startFeatureProperties

        return featureProperties

    @dgl_timer_enabled
    def createDetailedSummary(self, folderPath, costAttribute, outputFilename):
        """
        Given a set of Geojson (Geometry type: LineString) files, read all the files from the given ``folderPath`` and
        sum all the attribute values (distance, speed_limit_time, day_avg_delay_time, midday_delay_time and
        rush_hour_delay_time) and create a simple features Geojson (Geometry type: LineString)
        with the summary information.

        :param folderPath: Folder containing the shortest path geojson features.
        :param outputFilename: Filename to give to the summary file.
        :return: None. Store the summary information in the folderPath with the name given in outputFilename.
        """
        Logger.getInstance().info("Start createDetailedSummary for: %s" % costAttribute)

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
                    Logger.getInstance().info(filemetadata)

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
                    Logger.getInstance().info(err)

        totals["totalFeatures"] = len(totals["features"])
        outputFilename = getEnglishMeaning(costAttribute) + "_" + outputFilename
        self.fileActions.writeFile(folderPath=summaryFolderPath, filename=outputFilename, data=totals)

    @dgl_timer_enabled
    def createGeneralSummary(self, startCoordinatesGeojsonFilename, endCoordinatesGeojsonFilename, costAttribute,
                             outputFolderPath, outputFilename):
        """
        Using the power of pgr_Dijsktra algorithm this function calculate the total routing cost for a pair of set of points.
        It differentiate if must to use one-to-one, one-to-many, many-to-one or many-to-many specific stored procedures from the pgrouting extension.

        :param startCoordinatesGeojsonFilename: Geojson file (Geometry type: MultiPoint) containing pair of points.
        :param outputFolderPath: URL to store the shortest path geojson features of each pair of points.
        :param costAttribute: Attribute to calculate the impedance of the Shortest Path algorithm.
        :param outputFolderPath: Folder containing the shortest path geojson features.
        :param outputFilename: Filename to give to the summary file.
        :return: None. Store the information in the ``outputFolderPath``.
        """
        Logger.getInstance().info("Start createGeneralSummary for: %s" % costAttribute)

        Logger.getInstance().info("Start merge additional layers")
        inputStartCoordinates = self.operations.mergeAdditionalLayers(
            originalJsonURL=startCoordinatesGeojsonFilename,
            outputFolderPath=outputFolderPath
        )

        inputEndCoordinates = self.operations.mergeAdditionalLayers(
            originalJsonURL=endCoordinatesGeojsonFilename,
            outputFolderPath=outputFolderPath
        )
        Logger.getInstance().info("End merge additional layers")

        Logger.getInstance().info("Start nearest vertices finding")
        epsgCode = self.operations.extractCRSWithGeopandas(startCoordinatesGeojsonFilename)
        # epsgCode = self.operations.extractCRSWithGeopandas(endCoordinatesGeojsonFilename)
        startVerticesID, startPointsFeaturesList = self.getVerticesID(inputStartCoordinates, epsgCode)
        endVerticesID, endPointsFeaturesList = self.getVerticesID(inputEndCoordinates, epsgCode)
        Logger.getInstance().info("End nearest vertices finding")

        totals = None

        Logger.getInstance().info("Start cost summary calculation")
        if len(startVerticesID) == 1 and len(endVerticesID) == 1:
            totals = self.transportMode.getTotalShortestPathCostOneToOne(
                startVertexID=startVerticesID[0],
                endVertexID=endVerticesID[0],
                costAttribute=costAttribute
            )
        elif len(startVerticesID) == 1 and len(endVerticesID) > 1:
            totals = self.transportMode.getTotalShortestPathCostOneToMany(
                startVertexID=startVerticesID[0],
                endVerticesID=endVerticesID,
                costAttribute=costAttribute
            )
        elif len(startVerticesID) > 1 and len(endVerticesID) == 1:
            totals = self.transportMode.getTotalShortestPathCostManyToOne(
                startVerticesID=startVerticesID,
                endVertexID=endVerticesID[0],
                costAttribute=costAttribute
            )
        elif len(startVerticesID) > 1 and len(endVerticesID) > 1:
            totals = self.transportMode.getTotalShortestPathCostManyToMany(
                startVerticesID=startVerticesID,
                endVerticesID=endVerticesID,
                costAttribute=costAttribute
            )
        Logger.getInstance().info("End cost summary calculation")

        costSummaryMap = self.createCostSummaryMap(totals)
        # summaryFeature = costSummaryMap[startVertexID][endVertexID]
        # KeyError: 125736

        counterStartPoints = 0
        counterEndPoints = 0

        ################################################################################################################
        # for featureShortPathSummary in totals["features"]:
        #     startVertexID = featureShortPathSummary["properties"]["start_vertex_id"]
        #     endVertexID = featureShortPathSummary["properties"]["end_vertex_id"]
        #     total_cost = featureShortPathSummary["properties"]["total_cost"]
        #     del featureShortPathSummary["properties"]["start_vertex_id"]
        #     del featureShortPathSummary["properties"]["end_vertex_id"]
        #     del featureShortPathSummary["properties"]["total_cost"]
        #
        #     startPointFeature = startPointsFeaturesList[counterStartPoints]
        #     endPointFeature = endPointsFeaturesList[counterEndPoints]
        #
        #     self.createCostSummaryWithAdditionalProperties(costAttribute, endPointFeature, endVertexID,
        #                                                    featureShortPathSummary, startPointFeature,
        #                                                    startVertexID,
        #                                                    total_cost)
        #     counterEndPoints += 1
        #     if counterEndPoints == len(endPointsFeaturesList):
        #         counterStartPoints += 1
        #         counterEndPoints = 0
        ################################################################################################################



        features = []
        ################################################################################################################
        # for startPointFeature in startPointsFeaturesList:
        #     for endPointFeature in endPointsFeaturesList:
        #         newFeature = createCostSummaryWithAdditionalProperties(costAttribute,
        #                                                                     startPointFeature,
        #                                                                     endPointFeature,
        #                                                                     costSummaryMap)
        #         if newFeature:
        #             features.append(newFeature)
        ################################################################################################################

        Logger.getInstance().info("Start createCostSummaryWithAdditionalProperties")
        with Parallel(n_jobs=int(getConfigurationProperties(section="PARALLELIZATION")["jobs"]),
                      backend="threading",
                      verbose=int(getConfigurationProperties(section="PARALLELIZATION")["verbose"])) as parallel:
            # while len(verticesID) <= len(geojson["features"]):
            parallel._print = parallel_job_print
            returns = parallel(delayed(createCostSummaryWithAdditionalProperties)(self,
                                                                                  costAttribute,
                                                                                  copy.deepcopy(startPointFeature),
                                                                                  copy.deepcopy(endPointFeature),
                                                                                  costSummaryMap)
                               for startPointFeature in startPointsFeaturesList
                               for endPointFeature in endPointsFeaturesList)

            for newFeature in returns:
                if newFeature:
                    features.append(newFeature)
                    # print(returns)

        Logger.getInstance().info("End createCostSummaryWithAdditionalProperties")

        ################################################################################################################

        totals["features"] = features
        if not outputFolderPath.endswith(os.sep):
            summaryFolderPath = outputFolderPath + os.sep + "summary" + os.sep
        else:
            summaryFolderPath = outputFolderPath + "summary" + os.sep

        outputFilename = getEnglishMeaning(costAttribute) + "_" + outputFilename
        self.fileActions.writeFile(folderPath=summaryFolderPath, filename=outputFilename, data=totals)

    @dgl_timer
    def getVerticesID(self, geojson, endEPSGCode):

        verticesID = []
        features = []

        # for feature in geojson["features"]:
        #     vertexID, feature = self.extractFeatureInformation(endEPSGCode, feature)
        #
        #     verticesID.append(vertexID)
        #     features.append(feature)
        with Parallel(n_jobs=int(getConfigurationProperties(section="PARALLELIZATION")["jobs"]),
                      backend="threading",
                      verbose=int(getConfigurationProperties(section="PARALLELIZATION")["verbose"])) as parallel:
            # while len(verticesID) <= len(geojson["features"]):
            parallel._print = parallel_job_print
            returns = parallel(
                delayed(extractFeatureInformation)(self, endEPSGCode, feature, self.transportMode, self.operations)
                for feature in geojson["features"])
            for vertexID, feature in returns:
                verticesID.append(vertexID)
                features.append(feature)
                # print(returns)

        return verticesID, features

    @dgl_timer
    def createCostSummaryMap(self, totals):
        """

        :param totals:
        :return:
        """
        """
            {
                "startId1": {
                    endId1: {feature1},
                    endId2: {feature2}
                }
                "startId2": {
                    endId1: {feature3},
                    endId2: {feature4}
                }
            }
            
        """

        costSummaryMap = {}
        for featureShortPathSummary in totals["features"]:
            startVertexID = featureShortPathSummary["properties"]["start_vertex_id"]
            endVertexID = featureShortPathSummary["properties"]["end_vertex_id"]
            if startVertexID not in costSummaryMap:
                costSummaryMap[startVertexID] = {}

            startVertexMap = costSummaryMap[startVertexID]
            startVertexMap[endVertexID] = featureShortPathSummary

        return costSummaryMap
