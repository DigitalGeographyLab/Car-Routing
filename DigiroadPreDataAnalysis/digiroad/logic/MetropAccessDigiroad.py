import numpy as np
import nvector as nv
import os
from pyproj import Proj, transform

# from src.digiroad.carRoutingExceptions import NotWFSDefinedException, NotURLDefinedException  # ONLY test purposes
from digiroad.carRoutingExceptions import NotWFSDefinedException, NotURLDefinedException
from digiroad.connection import FileActions
from digiroad.entities import Point
from digiroad.util import CostAttributes, GeometryType, getEnglishMeaning


class MetropAccessDigiroadApplication:
    def __init__(self):
        self.fileActions = FileActions()

    def calculateTotalTimeTravel(self, wfsServiceProvider=None, inputCoordinatesGeojsonFilename=None,
                                 outputFolderPath=None, costAttribute=CostAttributes.DISTANCE):
        """
        Given a set of pair points and the ``cost attribute``, calculate the shortest path between each of them and
        store the Shortest Path Geojson file in the ``outputFolderPath``.

        :param wfsServiceProvider: WFS Service Provider data connection
        :param inputCoordinatesGeojsonFilename: Geojson file (Geometry type: MultiPoint) containing pair of points.
        :param outputFolderPath: URL to store the shortest path geojson features of each pair of points.
        :param costAttribute: Attribute to calculate the impedance of the Shortest Path algorithm.
        :return: None. Store the information in the ``outputFolderPath``.
        """

        if not wfsServiceProvider:
            raise NotWFSDefinedException()
        if not inputCoordinatesGeojsonFilename or not outputFolderPath:
            raise NotURLDefinedException()

        outputFolderPath = outputFolderPath + os.sep + "geoms" + os.sep + getEnglishMeaning(costAttribute) + os.sep

        self.fileActions.deleteFolder(path=outputFolderPath)

        inputCoordinates = self.fileActions.readMultiPointJson(inputCoordinatesGeojsonFilename)

        filename = "shortestPath"
        extension = "geojson"

        epsgCode = inputCoordinates["crs"]["properties"]["name"].split(":")[-3] + ":" + \
                   inputCoordinates["crs"]["properties"]["name"].split(":")[-1]

        for startPointfeature in inputCoordinates["features"]:
            startCoordinates = startPointfeature["geometry"]["coordinates"][0]
            endCoordinates = startPointfeature["geometry"]["coordinates"][1]

            startPoint = Point(latitute=startCoordinates[0],
                               longitude=startCoordinates[1],
                               crs=epsgCode)
            endPoint = Point(latitute=endCoordinates[0],
                             longitude=endCoordinates[1],
                             crs=epsgCode)

            startPointNearestVertexGeojson = wfsServiceProvider.getNearestCarRoutableVertexFromAPoint(startPoint)
            endPointNearestVertexGeojson = wfsServiceProvider.getNearestCarRoutableVertexFromAPoint(endPoint)

            startPointfeature = startPointNearestVertexGeojson["features"][0]
            startNearestVertexCoordinates = startPointfeature["geometry"]["coordinates"][0]
            epsgCodeNearestVertexCoordinates = startPointNearestVertexGeojson["crs"]["properties"]["name"].split(":")[
                                                   -3] + ":" + \
                                               startPointNearestVertexGeojson["crs"]["properties"]["name"].split(":")[
                                                   -1]
            nearestStartPoint = Point(latitute=startNearestVertexCoordinates[1],
                                      longitude=startNearestVertexCoordinates[0],
                                      crs=epsgCodeNearestVertexCoordinates)
            startVertexId = startPointfeature["id"].split(".")[1]

            endPointFeature = endPointNearestVertexGeojson["features"][0]
            endNearestVertexCoordinates = endPointFeature["geometry"]["coordinates"][0]
            epsgCodeNearestVertexCoordinates = endPointNearestVertexGeojson["crs"]["properties"]["name"].split(":")[
                                                   -3] + ":" + \
                                               endPointNearestVertexGeojson["crs"]["properties"]["name"].split(":")[-1]
            nearestEndPoint = Point(latitute=endNearestVertexCoordinates[1],
                                    longitude=endNearestVertexCoordinates[0],
                                    crs=epsgCodeNearestVertexCoordinates)
            endVertexId = endPointFeature["id"].split(".")[1]

            shortestPath = wfsServiceProvider.getShortestPath(startVertexId=startVertexId, endVertexId=endVertexId,
                                                              cost=costAttribute)

            euclideanDistanceStartPoint = self.calculateEuclideanDistance(startPoint, nearestStartPoint)
            euclideanDistanceEndPoint = self.calculateEuclideanDistance(endPoint, nearestEndPoint)

            shortestPath["overallProperties"] = {
                "selectedStartCoordinates": [startPoint.getLongitude(), startPoint.getLatitude()],
                "selectedEndCoordinates": [endPoint.getLongitude(), endPoint.getLatitude()],
                "euclideanDistanceStartPoint": euclideanDistanceStartPoint,
                "nearestStartCoordinates": [nearestStartPoint.getLongitude(), nearestStartPoint.getLatitude()],
                "nearestEndCoordinates": [nearestEndPoint.getLongitude(), nearestEndPoint.getLatitude()],
                "euclideanDistanceEndPoint": euclideanDistanceEndPoint
            }

            completeFilename = "%s_%s_%s_%s.%s" % (
                filename, getEnglishMeaning(costAttribute), startVertexId, endVertexId, extension)
            self.fileActions.writeFile(folderPath=outputFolderPath, filename=completeFilename, data=shortestPath)

    def calculateEuclideanDistance(self, startPoint=Point, endPoint=Point):
        """
        Calculate the distances between two points in meters.

        :param startPoint: latitude and longitud of the first point, must contain the CRS in which is given the coordinates
        :param endPoint: latitude and longitud of the second point, must contain the CRS in which is given the coordinates
        :return: Euclidean distance between the two points in meters.
        """

        startPointTransformed = self.transformPoint(startPoint)
        endPointTransformed = self.transformPoint(endPoint)

        wgs84 = nv.FrameE(name='WGS84')
        point1 = wgs84.GeoPoint(latitude=startPointTransformed.getLatitude(),
                                longitude=startPointTransformed.getLongitude(),
                                degrees=True)
        point2 = wgs84.GeoPoint(latitude=endPointTransformed.getLatitude(),
                                longitude=endPointTransformed.getLongitude(),
                                degrees=True)
        ellipsoidalDistance, _azi1, _azi2 = point1.distance_and_azimuth(point2)
        p_12_E = point2.to_ecef_vector() - point1.to_ecef_vector()
        euclideanDistance = np.linalg.norm(p_12_E.pvector, axis=0)[0]

        return euclideanDistance

    def transformPoint(self, point, targetEPSGCode="epsg:4326"):
        """
        Coordinates Transform from one CRS to another CRS.
         
        :param point: 
        :param targetEPSGCode:
        :return:
        """

        inProj = Proj(init=point.getCRS())
        outProj = Proj(init=targetEPSGCode)

        lng, lat = transform(inProj, outProj, point.getLongitude(), point.getLatitude())

        return Point(latitute=lat, longitude=lng, crs=targetEPSGCode)

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

                filemetadata = file.split("_")
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
                        "startVertexId": filemetadata[2],
                        "endVertexId": filemetadata[3].replace(".geojson", ""),
                        "costAttribute": filemetadata[1],
                        "selectedStartCoordinates": shortestPath["overallProperties"]["selectedStartCoordinates"],
                        "selectedEndCoordinates": shortestPath["overallProperties"]["selectedEndCoordinates"],
                        "nearestStartCoordinates": shortestPath["overallProperties"]["nearestStartCoordinates"],
                        "nearestEndCoordinates": shortestPath["overallProperties"]["nearestEndCoordinates"],
                        "euclideanDistanceStartPoint": shortestPath["overallProperties"]["euclideanDistanceStartPoint"],
                        "euclideanDistanceEndPoint": shortestPath["overallProperties"]["euclideanDistanceEndPoint"]
                    }
                }

                startPoints = None
                endPoints = None

                for segmentFeature in shortestPath["features"]:
                    for key in segmentFeature["properties"]:
                        if key == "seq" and segmentFeature["properties"][key] == 1:
                            # Sequence one is the first linestring geometry in the path
                            startPoints = segmentFeature["geometry"]["coordinates"]
                        if key == "seq" and segmentFeature["properties"][key] == shortestPath["totalFeatures"]:
                            # The last sequence is the last linestring geometry in the path
                            endPoints = segmentFeature["geometry"]["coordinates"]

                        if key not in ["id", "direction", "seq"]:
                            if key not in newSummaryFeature["properties"]:
                                newSummaryFeature["properties"][key] = 0

                            newSummaryFeature["properties"][key] = newSummaryFeature["properties"][key] + \
                                                                   segmentFeature["properties"][key]

                newSummaryFeature["geometry"]["coordinates"] = newSummaryFeature["geometry"]["coordinates"] + \
                                                               startPoints
                newSummaryFeature["geometry"]["coordinates"] = newSummaryFeature["geometry"]["coordinates"] + \
                                                               endPoints
                totals["features"].append(newSummaryFeature)

        totals["totalFeatures"] = len(totals["features"])
        outputFilename = getEnglishMeaning(costAttribute) + "_" + outputFilename
        self.fileActions.writeFile(folderPath=summaryFolderPath, filename=outputFilename, data=totals)
