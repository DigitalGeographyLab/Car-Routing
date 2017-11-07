import getopt
import sys

import configparser
import os

from digiroad.carRoutingExceptions import FileNotFoundException
from digiroad.connection import ReadData
from digiroad.logic.MetropAccessDigiroad import MetropAccessDigiroadApplication


def main():
    argv = sys.argv[1:]
    opts, args = getopt.getopt(argv, "c:s:", ["coordinates=", "shortestPathOutput="])

    inputCoordinatesGeojsonFilename = None
    outputShortestGeojsonPathLayerFilename = None

    for opt, arg in opts:
        print "options: %s, arg: %s" % (opt, arg)
        if opt == '-h':
            raise FileNotFoundException()

        if opt in ("-c", "--coordinates"):
            inputCoordinatesGeojsonFilename = arg

        if opt in ("-s", "--shortestPathOutput"):
            outputShortestGeojsonPathLayerFilename = arg

    config = configparser.ConfigParser()
    dir = os.getcwd()

    config.read('../src/resources/configuration.properties')

    starter = MetropAccessDigiroadApplication()
    readData = ReadData(wfs_url=config["WFS_CONFIG"]["wfs_url"],
                        nearestVertexTypeName=config["WFS_CONFIG"]["nearestVertexTypeName"],
                        shortestPathTypeName=config["WFS_CONFIG"]["shortestPathTypeName"],
                        outputFormat=config["WFS_CONFIG"]["outputFormat"])

    starter.calculateTotalTimeTravel(wfsServiceProvider=readData,
                                     inputCoordinatesGeojsonFilename=inputCoordinatesGeojsonFilename,
                                     outputFolderPath=outputShortestGeojsonPathLayerFilename)

    starter.createSummary(outputShortestGeojsonPathLayerFilename, "metroAccessDigiroadSummary.geojson")
