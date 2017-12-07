class Point:
    def __init__(self, latitute, longitude, crs):
        self.__latitude = latitute
        self.__longitude = longitude
        self.__crs = crs

    def getLatitude(self):
        return self.__latitude

    def getLongitude(self):
        return self.__longitude

    def getCRS(self):
        return self.__crs

    def setLatitude(self, latitute):
        self.__latitude = latitute

    def setLongitude(self, longitude):
        self.__longitude = longitude

    def setCRS(self, crs):
        self.__crs = crs
