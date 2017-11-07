import json
import os
import shutil

# from src.digiroad.carRoutingExceptions import FileNotFoundException, NotWFSDefinedException, NotURLDefinedException # ONLY test purposes
from digiroad.carRoutingExceptions import NotWFSDefinedException, NotURLDefinedException
from digiroad.enumerations import CostAttributes


class MetropAccessDigiroadApplication:
    def __init__(self):
        pass

    def calculateTotalTimeTravel(self, wfsServiceProvider=None, inputCoordinatesGeojsonFilename=None,
                                 outputFolderPath=None, costAttribute=CostAttributes.DISTANCE):
        if not wfsServiceProvider:
            raise NotWFSDefinedException()
        if not inputCoordinatesGeojsonFilename or not outputFolderPath:
            raise NotURLDefinedException()

        self.deleteFolder(path=outputFolderPath)

        inputCoordinates = wfsServiceProvider.readMultiPointJson(inputCoordinatesGeojsonFilename)

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

            newFeature = startPointNearestVertexCoordinates["features"][0]
            # lat = newFeature["geometry"]["coordinates"][1]
            # lng = newFeature["geometry"]["coordinates"][0]
            startVertexId = newFeature["id"].split(".")[1]

            newFeature = endPointNearestVertexCoordinates["features"][0]
            # lat = newFeature["geometry"]["coordinates"][1]
            # lng = newFeature["geometry"]["coordinates"][0]
            endVertexId = newFeature["id"].split(".")[1]

            shortestPath = wfsServiceProvider.getShortestPath(startVertexId=startVertexId, endVertexId=endVertexId,
                                                              cost=costAttribute)

            completeFilename = "%s_%s_%s.%s" % (filename, startVertexId, endVertexId, extension)
            self.writeFile(folderPath=outputFolderPath, filename=completeFilename, data=shortestPath)

    def createSummary(self, folderPath, outputFilename):
        totals = {"features": []}

        for file in os.listdir(folderPath):
            if file.endswith(".geojson"):

                filemetadata = file.split("_")
                if len(filemetadata) < 2:
                    print filemetadata

                newSummaryFeature = {
                    "geometry": {
                        "coordinates": [
                        ],
                        "type": "LineString"
                    },
                    "properties": {
                        "startVertexId": filemetadata[1],
                        "endVertexId": filemetadata[2].replace(".geojson", "")
                    }
                }

                shortestPath = self.readJsonFile(filePath=folderPath + file)
                startPoints = None
                endPoints = None

                for segmentFeature in shortestPath["features"]:
                    for key in segmentFeature["properties"]:
                        if key == "seq" and segmentFeature["properties"][key] == 1:
                            startPoints = segmentFeature["geometry"]["coordinates"]
                        if key == "seq" and segmentFeature["properties"][key] == shortestPath["totalFeatures"]:
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

        self.writeFile(folderPath=folderPath, filename=outputFilename, data=totals)

    def readJsonFile(self, filePath):
        with open(filePath, 'r') as outfile:
            data = json.load(outfile)
        return data

    def writeFile(self, folderPath, filename, data):
        if not os.path.exists(folderPath):
            os.makedirs(folderPath)

        fileURL = folderPath + "/%s" % filename

        with open(fileURL, 'w+') as outfile:
            json.dump(data, outfile, sort_keys=True)

    def deleteFolder(self, path):
        print "Deleting FOLDER %s" % path
        if os.path.exists(path):
            shutil.rmtree(path)
        print "The FOLDER %s was deleted" % path