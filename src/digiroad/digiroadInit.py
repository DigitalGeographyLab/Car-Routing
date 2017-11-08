import getopt
import sys

import configparser
import os

from digiroad.connection import WFSServiceProvider
from digiroad.logic.MetropAccessDigiroad import MetropAccessDigiroadApplication


def main():
    """
    Read the arguments written in the command line to read the input coordinates from a
    Geojson file (a set of pair points) and the location (URL) to store the Shortest Path geojson features for each
    pair of points.

    Call the ``calculateTotalTimeTravel`` from the WFSServiceProvider configured
    with the parameters in './resources/configuration.properties' and calculate the shortest path for each
    pair of points and store a Geojson file per each of them.

    After that, call the function ``createSummary`` to summarize the total time expend to go from one point to another
    for each of the different impedance attribute (cost).

    :return: None. All the information is stored in the ``shortestPathOutput`` URL.
    """
    argv = sys.argv[1:]
    opts, args = getopt.getopt(argv, "c:s:", ["coordinates=", "shortestPathOutput="])

    inputCoordinatesGeojsonFilename = None
    outputShortestGeojsonPathLayerFilename = None

    for opt, arg in opts:
        print "options: %s, arg: %s" % (opt, arg)

        if opt in ("-c", "--coordinates"):
            inputCoordinatesGeojsonFilename = arg

        if opt in ("-s", "--shortestPathOutput"):
            outputShortestGeojsonPathLayerFilename = arg

    config = configparser.ConfigParser()
    dir = os.getcwd()

    config.read('../src/resources/configuration.properties')

    starter = MetropAccessDigiroadApplication()
    wfsServiceProvider = WFSServiceProvider(wfs_url=config["WFS_CONFIG"]["wfs_url"],
                                            nearestVertexTypeName=config["WFS_CONFIG"]["nearestVertexTypeName"],
                                            shortestPathTypeName=config["WFS_CONFIG"]["shortestPathTypeName"],
                                            outputFormat=config["WFS_CONFIG"]["outputFormat"])

    starter.calculateTotalTimeTravel(wfsServiceProvider=wfsServiceProvider,
                                     inputCoordinatesGeojsonFilename=inputCoordinatesGeojsonFilename,
                                     outputFolderPath=outputShortestGeojsonPathLayerFilename)

    starter.createSummary(outputShortestGeojsonPathLayerFilename, "metroAccessDigiroadSummary.geojson")
