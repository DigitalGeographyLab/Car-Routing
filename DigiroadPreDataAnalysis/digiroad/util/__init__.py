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

GeometryType = enum(MULTI_POINT='MultiPoint', LINE_STRING='LineString')


def getEnglishMeaning(cost_attribute=None):
    return carRountingDictionary[cost_attribute]
