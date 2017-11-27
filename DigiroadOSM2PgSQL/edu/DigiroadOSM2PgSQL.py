import getopt
import os
import sys

import configparser

from edu.digiroad.enumerations import OsmosisCommands
from edu.digiroad.osmsync import DigiroadOsmosis
from edu.digiroad.osmsync.connection import DigiroadOSMConnection


def main():
    """
    Read the arguments written in the command line.
    Download the OSM/PBF file from an external URL.
    Split the OSM/PBF file in the new region.
    Finally, upload the OSM/PBF data into the database with the highways and railways information.

    :return: None.
    """
    argv = sys.argv[1:]
    opts, args = getopt.getopt(argv, "i:d:o:l:r:t:b:",
                               [
                                   "osmurl=", "databasename=", "outputfolder=",
                                   "left=", "right=", "top=", "bottom="
                               ])

    osmURL = None
    databaseName = None
    outputfolder = None
    left = 0
    right = 0
    top = 0
    bottom = 0

    for opt, arg in opts:
        print("options: %s, arg: %s" % (opt, arg))

        if opt in ("-i", "--osmurl"):
            osmURL = arg

        if opt in ("-d", "--databasename"):
            databaseName = arg

        if opt in ("-o", "--outputfolder"):
            outputfolder = arg

        if opt in ("-l", "--left"):
            left = arg

        if opt in ("-r", "--right"):
            right = arg

        if opt in ("-t", "--top"):
            top = arg

        if opt in ("-b", "--bottom"):
            bottom = arg

    config = configparser.ConfigParser()
    dir = os.getcwd()

    config.read('edu/resources/configuration.properties')

    if outputfolder and not outputfolder.endswith(os.sep):
        outputfolder = outputfolder + os.sep
        print("new folder: %s" % outputfolder)

    connection = DigiroadOSMConnection()
    downloadedfile = connection.download(osmURL=osmURL, outputPath=outputfolder)

    osmosis = DigiroadOsmosis()
    outputfile = osmosis.subRegionSplitter(osmFilePath=downloadedfile,
                                           osmSubregionPath=outputfolder,
                                           left=left,
                                           right=right,
                                           top=top,
                                           bottom=bottom)

    # connection.uploadOSMFile2PgSQLDatabase(username=config["OSM2PGSQL_CONFIG"]["username"],
    #                                        password=config["OSM2PGSQL_CONFIG"]["password"],
    #                                        databaseName=databaseName,
    #                                        styleURL=config["OSM2PGSQL_CONFIG"]["osm2pgsqlStyle"],
    #                                        inputFile=outputfile,
    #                                        fileFormat=OsmosisCommands.PBF)

    connection.imposmFile2PgSQLDatabase(username=config["OSM2PGSQL_CONFIG"]["username"],
                                        password=config["OSM2PGSQL_CONFIG"]["password"],
                                        hostname=config["OSM2PGSQL_CONFIG"]["hostname"],
                                        port=config["OSM2PGSQL_CONFIG"]["port"],
                                        databaseName=databaseName,
                                        inputFile=outputfile,
                                        mappingFile=config["OSM2PGSQL_CONFIG"]["mapping"])
