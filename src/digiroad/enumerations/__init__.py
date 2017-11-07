def enum(**enums):
    return type('Enum', (), enums)


CostAttributes = enum(DISTANCE='pituus', SPEED_LIMIT_TIME='digiroa_aa', DAY_AVG_DELAY_TIME='kokopva_aa',
                      MIDDAY_DELAY_TIME='keskpva_aa', RUSH_HOUR_DELAY='ruuhka_aa')
