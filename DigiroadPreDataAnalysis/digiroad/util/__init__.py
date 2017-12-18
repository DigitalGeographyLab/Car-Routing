import configparser
import datetime
import os
import time


def enum(**enums):
    return type('Enum', (), enums)


carRountingDictionary = {
    "pituus": "distance",
    "digiroa_aa": "speed_limit_time",
    "kokopva_aa": "day_average_delay_time",
    "keskpva_aa": "midday_delay_time",
    "ruuhka_aa": "rush_hour_delay_time"
}

CostAttributes = enum(DISTANCE='pituus', SPEED_LIMIT_TIME='digiroa_aa', DAY_AVG_DELAY_TIME='kokopva_aa',
                      MIDDAY_DELAY_TIME='keskpva_aa', RUSH_HOUR_DELAY='ruuhka_aa')

GeometryType = enum(POINT="Point", MULTI_POINT='MultiPoint', LINE_STRING='LineString')

PostfixAttribute = enum(EUCLIDEAN_DISTANCE="EuclideanDistance", AVG_WALKING_DISTANCE="AVGWalkingDistance",
                        WALKING_TIME="WalkingTime", PARKING_TIME="ParkingTime")


def getEnglishMeaning(cost_attribute=None):
    return carRountingDictionary[cost_attribute]


def getFormattedDatetime(timemilis=time.time(), format='%Y-%m-%d %H:%M:%S'):
    formattedDatetime = datetime.datetime.fromtimestamp(timemilis).strftime(format)
    return formattedDatetime


def timeDifference(startTime, endTime):
    totalTime = (endTime - startTime) / 60  # min
    return totalTime


def getConfigurationProperties(section="WFS_CONFIG"):
    config = configparser.ConfigParser()
    configurationPath = os.getcwd() + "%resources%configuration.properties".replace("%", os.sep)
    config.read(configurationPath)
    return config[section]


class AbstractLinkedList(object):
    def __init__(self):
        self._next = None

    def hasNext(self):
        return self._next is not None

    def next(self):
        self._next

    def setNext(self, next):
        self._next = next


class Node:
    def __init__(self, item):
        """
        A node contains an item and a possible next node.
        :param item: The referenced item.
        """
        self._item = item
        self._next = None

    def getItem(self):
        return self._item

    def setItem(self, item):
        self._item = item

    def getNext(self):
        return self._next

    def setNext(self, next):
        self._next = next


class LinkedList(AbstractLinkedList):
    def __init__(self):
        """
        Linked List implementation.

        The _head is the first node in the linked list.
        _next refers to the possible next node into the linked list.
        And the _tail is the last node added into the linked list.
        """
        self._head = None
        self._next = None
        self._tail = None

    def hasNext(self):
        """
        Veryfy if there is a possible next node in the queue of the linked list.

        :return: True if there is a next node.
        """
        if self._next:
            return True

        return False

    def next(self):
        """
        :return: The next available item in the queue of the linked list.
        """
        item = self._next.getItem()
        self._next = self._next.getNext()
        return item

    def add(self, newItem):
        """
        Add new items into the linked list. The _tail is moving forward and create a new node ecah time that a new item
        is added.

        :param newItem: Item to be added.
        """
        if self._head is None:
            self._head = Node(newItem)
            self._next = self._head
            self._tail = self._head
        else:
            node = Node(newItem)
            self._tail.setNext(node)
            self._tail = node

    def restart(self):
        """
        Move the linked list to its initial node.
        """
        self._next = self._head
        self._tail = self._head
