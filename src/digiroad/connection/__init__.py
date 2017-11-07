import json

from owslib.util import openURL

# import src.digiroad.carRoutingExceptions as exc # ONLY test purposes
import digiroad.carRoutingExceptions as exc


class ReadData:
    def __init__(self, wfs_url="http://localhost:8080/geoserver/wfs?", nearestVertexTypeName="",
                 shortestPathTypeName="", outputFormat=""):
        self.shortestPathTypeName = shortestPathTypeName
        self.__geoJson = None
        self.wfs_url = wfs_url
        self.typeName = nearestVertexTypeName
        self.outputFormat = outputFormat

    def readJson(self, url):
        data = None
        with open(url) as f:
            data = json.load(f)

        return data

    def readMultiPointJson(self, url):
        data = None
        with open(url) as f:
            data = json.load(f)

        self.checkGeometry(data)

        return data

    # def getGeoJson(self):
    #     return self.__geoJson
    #
    # def setGeoJson(self, geojson):
    #     self.__geoJson = geojson

    def checkGeometry(self, data):
        for feature in data["data"]["features"]:
            if feature["geometry"]["type"] != "MultiPoint":
                raise exc.NotMultiPointGeometryException("")

    def getNearestVertextFromAPoint(self, coordinates):
        url = self.wfs_url + "service=WFS&version=1.0.0&request=GetFeature&typeName=%s&outputformat=%s&viewparams=x:%s;y:%s" % (
            self.typeName, self.outputFormat, str(
                coordinates["lng"]), str(coordinates["lat"]))

        # wfs11 = WebFeatureService(url="http://localhost:8080/geoserver/wfs", version="1.1.0")
        # return wfs11.getfeature(typename='tutorial:dgl_nearest_vertex',
        #                         outputFormat="application/json",
        #                         filter="viewparams=x:" + str(coordinates["lng"]) + ';y:' + str(coordinates["lat"]))

        u = openURL(url)
        return json.loads(u.read())

    def getShortestPath(self, startVertexId, endVertexId, cost):
        url = self.wfs_url + "service=WFS&version=1.0.0&request=GetFeature&typeName=%s&outputformat=%s&viewparams=source:%s;target:%s;cost:%s" % (
            self.shortestPathTypeName, self.outputFormat,
            startVertexId, endVertexId, cost)

        u = openURL(url)
        return json.loads(u.read())
