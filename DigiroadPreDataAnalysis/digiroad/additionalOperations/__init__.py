import abc

from digiroad.carRoutingExceptions import deprecated
from digiroad.entities import Point
from digiroad.logic.Operations import Operations
from digiroad.util import getConfigurationProperties, PostfixAttribute, FileActions


class AbstractAdditionalLayerOperation(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, executionOrder=-1):
        """
        Abstract class to define new operations over the start and end point features properties.

        :param executionOrder: order in which must be executed the new operation.
        """
        self._executionOrder = executionOrder
        self.operations = Operations(FileActions())

    @abc.abstractmethod
    def runOperation(self, featureJson, prefix=""):
        """
        Method to be implemented to add the new operation behaviour.

        :param featureJson: feature properties of the start or end point.
        :param prefix: "startPoint_" or "endPoint_".
        :return: Dictionary/json containing the result values.
        """
        raise NotImplementedError("Should have implemented this")

    @deprecated
    def getExecutionOrder(self):
        return self._executionOrder


class EuclideanDistanceOperation(AbstractAdditionalLayerOperation):
    def __init__(self):
        super(EuclideanDistanceOperation, self).__init__(1)
        self.selectedPointCoordinatesAttribute, self.nearestVertexCoordinatesAttribute, self.coordinatesCRSAttribute = tuple(
            getConfigurationProperties("GEOJSON_LAYERS_ATTRIBUTES")["points_attributes"].split(","))

    def runOperation(self, featureJson, prefix=""):
        """
        Calculate the euclidean distance between the selected point and its nearest routable vertex.

        :param featureJson: feature properties of the start or end point.
        :param prefix: "startPoint_" or "endPoint_".
        :return: Euclidean distance.
        """
        startPoint = Point(
            latitute=featureJson["properties"][self.selectedPointCoordinatesAttribute][1],
            longitude=featureJson["properties"][self.selectedPointCoordinatesAttribute][0],
            epsgCode=featureJson["properties"][self.coordinatesCRSAttribute]
        )
        nearestStartPoint = Point(
            latitute=featureJson["properties"][self.nearestVertexCoordinatesAttribute][1],
            longitude=featureJson["properties"][self.nearestVertexCoordinatesAttribute][0],
            epsgCode=featureJson["properties"][self.coordinatesCRSAttribute]
        )
        newProperties = {
            prefix + PostfixAttribute.EUCLIDEAN_DISTANCE: self.operations.calculateEuclideanDistance(
                startPoint=startPoint,
                endPoint=nearestStartPoint
            )
        }
        return newProperties


class WalkingTimeOperation(AbstractAdditionalLayerOperation):
    def __init__(self):
        super(WalkingTimeOperation, self).__init__(2)
        self.walkingDistanceAttribute, = tuple(
            getConfigurationProperties("GEOJSON_LAYERS_ATTRIBUTES")["walking_distance_attributes"].split(","))
        self.walkingSpeed = float(getConfigurationProperties("WFS_CONFIG")["walkingSpeed"])

    def runOperation(self, featureJson, prefix=""):
        """
        Calculate the time spend to walk the euclidean distance betweent the selected point and its nearest vertex and
        the average walking time based on the walking distance layer data.

        :param featureJson: feature properties of the start or end point.
        :param prefix: "startPoint_" or "endPoint_".
        :return: The euclidian walking time and average walking time.
        """
        euclideanDistanceStartPoint = 0
        for property in featureJson["properties"]:
            if property.endswith(PostfixAttribute.EUCLIDEAN_DISTANCE):
                euclideanDistanceStartPoint = featureJson["properties"][property]
                break

        walkingDistance = featureJson["properties"][self.walkingDistanceAttribute]
        if not walkingDistance:
            walkingDistance = 0

        euclideanDistanceTime = self.operations.calculateTime(
            euclideanDistanceStartPoint,
            self.walkingSpeed
        )

        walkingDistanceTime = self.operations.calculateTime(
            walkingDistance,
            self.walkingSpeed
        )

        newProperties = {
            prefix + PostfixAttribute.EUCLIDEAN_DISTANCE + PostfixAttribute.WALKING_TIME: euclideanDistanceTime,
            prefix + PostfixAttribute.AVG_WALKING_DISTANCE + PostfixAttribute.WALKING_TIME: walkingDistanceTime,
        }
        return newProperties


class ParkingTimeOperation(AbstractAdditionalLayerOperation):
    def __init__(self):
        super(ParkingTimeOperation, self).__init__(3)
        self.parkingTimeAttribute, = tuple(
            getConfigurationProperties("GEOJSON_LAYERS_ATTRIBUTES")["parking_time_attributes"].split(","))

    def runOperation(self, featureJson, prefix=""):
        """
        Add the parking time to the selected point.

        :param featureJson: feature properties of the start or end point.
        :param prefix: "startPoint_" or "endPoint_".
        :return: Parking time.
        """

        parkingTime = None
        if featureJson["properties"][self.parkingTimeAttribute]:
            parkingTime = float(featureJson["properties"][self.parkingTimeAttribute])

        newProperties = {
            prefix + PostfixAttribute.PARKING_TIME: parkingTime
        }
        return newProperties
