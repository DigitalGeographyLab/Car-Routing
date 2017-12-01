import getopt
import os
import sys

import configparser

from digiroad.carRoutingExceptions import ImpedanceAttributeNotDefinedException, NotParameterGivenException
from digiroad.connection import WFSServiceProvider
from digiroad.logic.MetropAccessDigiroad import MetropAccessDigiroadApplication
from digiroad.util import CostAttributes


def printHelp():
    print (
        "DigiroadPreDataAnalysis tool\n"
        "\n\t[--help]: Print information about the parameters necessary to run the tool."
        "\n\t[-c, --coordinates]: Geojson file containing all the pair of points to calculate the shortest path between them."
        "\n\t[-s, --shortestPathFolder]: The final destination where the output geojson and summary files will be located."
        "\n\t[-i, --impedance]: The impedance/cost attribute to calculate the shortest path."
        "\n\t[--all]: Calculate the shortest path to all the impedance/cost attributes."
        "\n\nImpedance values allowed:"
        "\n\tDISTANCE"
        "\n\tSPEED_LIMIT_TIME"
        "\n\tDAY_AVG_DELAY_TIME"
        "\n\tMIDDAY_DELAY_TIME"
        "\n\tRUSH_HOUR_DELAY"
    )


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
    opts, args = getopt.getopt(argv, "c:s:i:", ["coordinates=", "shortestPathFolder=", "impedance", "all", "help"])

    inputCoordinatesGeojsonFilename = None
    outputShortestGeojsonPathLayerFilename = None
    # impedance = CostAttributes.DISTANCE
    impedance = None
    impedances = {
        "DISTANCE": CostAttributes.DISTANCE,
        "SPEED_LIMIT_TIME": CostAttributes.SPEED_LIMIT_TIME,
        "DAY_AVG_DELAY_TIME": CostAttributes.DAY_AVG_DELAY_TIME,
        "MIDDAY_DELAY_TIME": CostAttributes.MIDDAY_DELAY_TIME,
        "RUSH_HOUR_DELAY": CostAttributes.RUSH_HOUR_DELAY
    }

    allImpedanceAttribute = False

    for opt, arg in opts:
        if opt in "--help":
            printHelp()
            return

        print("options: %s, arg: %s" % (opt, arg))

        if opt in ("-c", "--coordinates"):
            inputCoordinatesGeojsonFilename = arg

        if opt in ("-s", "--shortestPathFolder"):
            outputShortestGeojsonPathLayerFilename = arg

        if opt in "--all":
            allImpedanceAttribute = True
        else:
            if opt in ("-i", "--impedance"):
                if arg not in impedances:
                    raise ImpedanceAttributeNotDefinedException(
                        "Use the paramenter -i or --impedance.\nValues allowed: DISTANCE, SPEED_LIMIT_TIME, DAY_AVG_DELAY_TIME, MIDDAY_DELAY_TIME, RUSH_HOUR_DELAY.\nThe parameter --all enable the analysis for all the impedance attributes.")

                impedance = impedances[arg]

    if not inputCoordinatesGeojsonFilename or not outputShortestGeojsonPathLayerFilename:
        raise NotParameterGivenException("Type --help for more information.")

    if not allImpedanceAttribute and not impedance:
        raise ImpedanceAttributeNotDefinedException(
            "Use the paramenter -i or --impedance.\nValues allowed: DISTANCE, SPEED_LIMIT_TIME, DAY_AVG_DELAY_TIME, MIDDAY_DELAY_TIME, RUSH_HOUR_DELAY.\nThe parameter --all enable the analysis for all the impedance attributes.")

    config = configparser.ConfigParser()
    dir = os.getcwd()

    config.read('../DigiroadPreDataAnalysis/resources/configuration.properties')

    starter = MetropAccessDigiroadApplication()
    wfsServiceProvider = WFSServiceProvider(wfs_url=config["WFS_CONFIG"]["wfs_url"],
                                            nearestVertexTypeName=config["WFS_CONFIG"]["nearestVertexTypeName"],
                                            shortestPathTypeName=config["WFS_CONFIG"]["shortestPathTypeName"],
                                            outputFormat=config["WFS_CONFIG"]["outputFormat"])

    if impedances and not allImpedanceAttribute:
        starter.calculateTotalTimeTravel(wfsServiceProvider=wfsServiceProvider,
                                         inputCoordinatesGeojsonFilename=inputCoordinatesGeojsonFilename,
                                         outputFolderPath=outputShortestGeojsonPathLayerFilename,
                                         costAttribute=impedance)
        starter.createSummary(outputShortestGeojsonPathLayerFilename, impedance, "metroAccessDigiroadSummary.geojson")

    if allImpedanceAttribute:
        for key in impedances:
            starter.calculateTotalTimeTravel(wfsServiceProvider=wfsServiceProvider,
                                             inputCoordinatesGeojsonFilename=inputCoordinatesGeojsonFilename,
                                             outputFolderPath=outputShortestGeojsonPathLayerFilename,
                                             costAttribute=impedances[key])
