import json

import os

import shutil
from owslib.util import openURL

# import DigiroadPreDataAnalysis.digiroad.carRoutingExceptions as exc  # ONLY test purposes
import digiroad.carRoutingExceptions as exc
from digiroad.util import GeometryType, transformPoint


class WFSServiceProvider:
    def __init__(self, wfs_url="http://localhost:8080/geoserver/wfs?",
                 nearestVertexTypeName="", nearestCarRoutingVertexTypeName="",
                 shortestPathTypeName="", outputFormat="", epsgCode="EPSG:3857"):
        self.shortestPathTypeName = shortestPathTypeName
        self.__geoJson = None
        self.wfs_url = wfs_url
        self.nearestVertexTypeName = nearestVertexTypeName
        self.nearestCarRoutingVertexTypeName = nearestCarRoutingVertexTypeName
        self.outputFormat = outputFormat
        self.epsgCode = epsgCode

    # def getGeoJson(self):
    #     return self.__geoJson
    #
    # def setGeoJson(self, geojson):
    #     self.__geoJson = geojson

    def getNearestVertexFromAPoint(self, coordinates):
        """
        From the WFS Service retrieve the nearest vertex from a given point coordinates.

        :param coordinates: Point coordinates. e.g [889213124.3123, 231234.2341]
        :return: Geojson (Geometry type: Point) with the nearest point coordinates.
        """
        coordinates = transformPoint(coordinates, self.epsgCode)

        url = self.wfs_url + "service=WFS&version=1.0.0&request=GetFeature&typeName=%s&outputformat=%s&viewparams=x:%s;y:%s" % (
            self.nearestVertexTypeName, self.outputFormat, str(
                coordinates.getLongitude()), str(coordinates.getLatitude()))

        return self.requestFeatures(url)

    def requestFeatures(self, url):
        u = openURL(url)
        # return json.loads(u.read())
        return json.loads(u.read().decode('utf-8'))

    def getNearestCarRoutableVertexFromAPoint(self, coordinates):
        """
        From the WFS Service retrieve the nearest car routing vertex from a given point coordinates.

        :param coordinates: Point coordinates. e.g [889213124.3123, 231234.2341]
        :return: Geojson (Geometry type: Point) with the nearest point coordinates.
        """
        url = self.wfs_url + "service=WFS&version=1.0.0&request=GetFeature&typeName=%s&outputformat=%s&viewparams=x:%s;y:%s" % (
            self.nearestCarRoutingVertexTypeName, self.outputFormat, str(
                coordinates.getLongitude()), str(coordinates.getLatitude()))

        return self.requestFeatures(url)

    def getShortestPath(self, startVertexId, endVertexId, cost):
        """
        From a pair of vertices (startVertexId, endVertexId) and based on the "cost" attribute,
        retrieve the shortest path by calling the WFS Service.

        :param startVertexId: Start vertex from the requested path.
        :param endVertexId: End vertex from the requested path.
        :param cost: Attribute to calculate the cost of the shortest path
        :return: Geojson (Geometry type: LineString) containing the segment features of the shortest path.
        """
        url = self.wfs_url + "service=WFS&version=1.0.0&request=GetFeature&typeName=%s&outputformat=%s&viewparams=source:%s;target:%s;cost:%s" % (
            self.shortestPathTypeName, self.outputFormat,
            startVertexId, endVertexId, cost)

        return self.requestFeatures(url)

    def getEPSGCode(self):
        return self.epsgCode

class FileActions:
    def readJson(self, url):
        """
        Read a json file
        :param url: URL for the Json file
        :return: json dictionary data
        """
        with open(url) as f:
            data = json.load(f)
        return data

    def readMultiPointJson(self, url):
        """
        Read a MultiPoint geometry geojson file, in case the file do not be a MultiPoint
        geometry, then an NotMultiPointGeometryException is thrown.

        :param url: URL for the Json file
        :return: json dictionary data
        """
        data = None
        with open(url) as f:
            data = json.load(f)

        self.checkGeometry(data, GeometryType.MULTI_POINT)

        return data

    def readPointJson(self, url):
        """
        Read a MultiPoint geometry geojson file, in case the file do not be a MultiPoint
        geometry, then an NotMultiPointGeometryException is thrown.

        :param url: URL for the Json file
        :return: json dictionary data
        """
        data = None
        with open(url) as f:
            data = json.load(f)

        self.checkGeometry(data, GeometryType.POINT)

        return data

    def checkGeometry(self, data, geometryType=GeometryType.MULTI_POINT):
        """
        Check the content of the Json to verify if it is a specific geoemtry type. By default is MultiPoint.
        In case the geojson do not be the given geometry type then an

        :param data: json dictionary
        :param geometryType: Geometry type (i.e. MultiPoint, LineString)
        :return: None
        """
        for feature in data["features"]:
            if feature["geometry"]["type"] != geometryType:
                raise exc.IncorrectGeometryTypeException("Expected %s" % geometryType)

    def writeFile(self, folderPath, filename, data):
        if not os.path.exists(folderPath):
            os.makedirs(folderPath)

        fileURL = folderPath + "/%s" % filename

        with open(fileURL, 'w+') as outfile:
            json.dump(data, outfile, sort_keys=True)

    def deleteFolder(self, path):
        print("Deleting FOLDER %s" % path)
        if os.path.exists(path):
            shutil.rmtree(path)
        print("The FOLDER %s was deleted" % path)
