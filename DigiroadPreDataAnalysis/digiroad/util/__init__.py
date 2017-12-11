import datetime
import time
from pyproj import Proj, transform
from digiroad.entities import Point


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


def getEnglishMeaning(cost_attribute=None):
    return carRountingDictionary[cost_attribute]


def transformPoint(point, targetEPSGCode="epsg:4326"):
    """
    Coordinates Transform from one CRS to another CRS.

    :param point:
    :param targetEPSGCode:
    :return:
    """
    if point.getEPSGCode().lower() == targetEPSGCode.lower():
        return point

    inProj = Proj(init=point.getEPSGCode())
    outProj = Proj(init=targetEPSGCode)

    lng, lat = transform(inProj, outProj, point.getLongitude(), point.getLatitude())

    return Point(latitute=lat, longitude=lng, epsgCode=targetEPSGCode)


def getFormattedDatetime(time, format="%Y-%m-%d %H:%M:%S"):
    st = datetime.datetime.fromtimestamp(time).strftime(format)
    return st
