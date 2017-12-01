import getopt
import os
import sys

import configparser

from digiroad.digiroadExceptions import NotParameterGivenException
from digiroad.osmsync import DigiroadOsmosis
from digiroad.osmsync.connection import DigiroadOSMConnection

from digiroad.enumerations import OsmosisCommands


def printHelp():
    print (
        "DigiroadOSM2PgSQL tool\n"
        "\n\t[--help]: Print information about the parameters necessary to run the tool."
        "\n\t[-i, --osmurl]: URL to download the OSM/PBF file."
        "\n\t[-o, --outputfolder]: The final destination where the downloaded file and clipped OSM/PBF file will be located."
        "\n\t[-d, --databasename]: Database name to store the exported OSM/PBF data."
        "\n\t[-l, --left]: Left latitude coordinate to clip the OSM/PBF file."
        "\n\t[-r, --right]: Right latitude coordinate to clip the OSM/PBF file."
        "\n\t[-t, --top]: Top latitude coordinate to clip the OSM/PBF file."
        "\n\t[-b, --bottom]: Bottom latitude coordinate to clip the OSM/PBF file."
        "\n\nConfiguration file:"
        "\n\tLocated in ./resources/configuration.properties.\n"
        "\n\t[OSM2PGSQL_CONFIG]"
        "\n\tosm2pgsqlStyle=<default.style> (in case you are using osm2pgsql instead of imposm)"
        "\n\tmapping=<.imposm3-mapping.json> (in case you are using imposm instead of osm2pgsql)"
        "\n\tdatabasename=<databasename> (this parameter replace the -d and --databasename parameters)"
        "\n\tusername=<username> (Database username)"
        "\n\tpassword=<password> (Database password)"
        "\n\thostname=localhost (Database URL)"
        "\n\tport=5432 (Database port)"
    )


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
                                   "left=", "right=", "top=", "bottom=", "help"
                               ])

    osmURL = None
    databaseName = None
    outputfolder = None
    left = 0
    right = 0
    top = 0
    bottom = 0

    for opt, arg in opts:
        if opt in "--help":
            printHelp()
            return
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

    if not osmURL or not outputfolder or not left or not right or not top or not bottom:
        raise NotParameterGivenException("Type --help for more information.")

    config = configparser.ConfigParser()
    dir = os.getcwd()

    config.read('resources%configuration.properties'.replace("%", os.sep))

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

    if not databaseName and not config["OSM2PGSQL_CONFIG"]["databasename"]:
        NotParameterGivenException("Type --help for more information.")
    else:
        if not databaseName:
            databaseName = config["OSM2PGSQL_CONFIG"]["databasename"]

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
