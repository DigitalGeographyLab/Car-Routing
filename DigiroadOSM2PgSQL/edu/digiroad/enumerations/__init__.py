def enum(**enums):
    return type('Enum', (), enums)


OsmosisCommands = enum(PBF='pbf', XML='xml')
