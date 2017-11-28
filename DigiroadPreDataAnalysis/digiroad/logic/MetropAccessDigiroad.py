import os

# from src.digiroad.carRoutingExceptions import NotWFSDefinedException, NotURLDefinedException  # ONLY test purposes
from digiroad.carRoutingExceptions import NotWFSDefinedException, NotURLDefinedException
from digiroad.connection import FileActions
from digiroad.enumerations import CostAttributes, GeometryType


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

        self.fileActions.deleteFolder(path=outputFolderPath)

        inputCoordinates = self.fileActions.readMultiPointJson(inputCoordinatesGeojsonFilename)

        filename = "shortestPath"
        extension = "geojson"
        for feature in inputCoordinates["data"]["features"]:
            startPoint = feature["geometry"]["coordinates"][0]
            endPoint = feature["geometry"]["coordinates"][1]
            lat = startPoint[0]
            lng = startPoint[1]
            startPointNearestVertexCoordinates = wfsServiceProvider.getNearestVertextFromAPoint({
                "lat": lat,
                "lng": lng
            })

            lat = endPoint[0]
            lng = endPoint[1]
            endPointNearestVertexCoordinates = wfsServiceProvider.getNearestVertextFromAPoint({
                "lat": lat,
                "lng": lng
            })

            startPoint = startPointNearestVertexCoordinates["features"][0]
            # lat = startPoint["geometry"]["coordinates"][1]
            # lng = startPoint["geometry"]["coordinates"][0]
            startVertexId = startPoint["id"].split(".")[1]

            endPoint = endPointNearestVertexCoordinates["features"][0]
            # lat = endPoint["geometry"]["coordinates"][1]
            # lng = endPoint["geometry"]["coordinates"][0]
            endVertexId = endPoint["id"].split(".")[1]

            shortestPath = wfsServiceProvider.getShortestPath(startVertexId=startVertexId, endVertexId=endVertexId,
                                                              cost=costAttribute)

            shortestPath["overallProperties"] = {
                "startCoordinates": startPoint["geometry"]["coordinates"],
                "endCoordinates": endPoint["geometry"]["coordinates"]
            }

            completeFilename = "%s_%s_%s.%s" % (filename, startVertexId, endVertexId, extension)
            self.fileActions.writeFile(folderPath=outputFolderPath, filename=completeFilename, data=shortestPath)

    def createSummary(self, folderPath, outputFilename):
        """
        Given a set of Geojson (Geometry type: LineString) files, read all the files from the given ``folderPath`` and
        sum all the attribute values (distance, speed_limit_time, day_avg_delay_time, midday_delay_time and
        rush_hour_delay_time) and create a simple features Geojson (Geometry type: LineString)
        with the summary information.

        :param folderPath: Folder containing the shortest path geojson features.
        :param outputFilename: Filename to give to the summary file.
        :return: None. Store the summary information in the folderPath with the name given in outputFilename.
        """
        totals = {
            "features": [],
            "totalFeatures": 0,
            "type": "FeatureCollection"
        }
        for file in os.listdir(folderPath):
            if file.endswith(".geojson") and file != "metroAccessDigiroadSummary.geojson":

                filemetadata = file.split("_")
                if len(filemetadata) < 2:
                    print(filemetadata)

                shortestPath = self.fileActions.readJson(url=folderPath + file)

                if "crs" not in totals:
                    totals["crs"] = shortestPath["crs"]

                newSummaryFeature = {
                    "geometry": {
                        "coordinates": [
                        ],
                        "type": GeometryType.LINE_STRING
                    },
                    "properties": {
                        "startVertexId": filemetadata[1],
                        "endVertexId": filemetadata[2].replace(".geojson", ""),
                        "startCoordinates": shortestPath["overallProperties"]["startCoordinates"],
                        "endCoordinates": shortestPath["overallProperties"]["endCoordinates"]
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
        self.fileActions.writeFile(folderPath=folderPath, filename=outputFilename, data=totals)
