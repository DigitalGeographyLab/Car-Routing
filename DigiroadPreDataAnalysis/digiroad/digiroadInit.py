import getopt
import sys

import os

from digiroad.carRoutingExceptions import ImpedanceAttributeNotDefinedException, NotParameterGivenException, \
    TransportModeNotDefinedException
from digiroad.connection.PostgisServiceProvider import PostgisServiceProvider
from digiroad.connection.WFSServiceProvider import WFSServiceProvider
from digiroad.logic.MetropAccessDigiroad import MetropAccessDigiroadApplication
from digiroad.transportMode.BicycleTransportMode import BicycleTransportMode
from digiroad.transportMode.PrivateCarTransportMode import PrivateCarTransportMode
from digiroad.util import CostAttributes, getConfigurationProperties, TransportModes, Logger, FileActions, \
    getFormattedDatetime


def printHelp():
    print(
        "DigiroadPreDataAnalysis tool\n"
        "\n\t[--help]: Print information about the parameters necessary to run the tool."
        "\n\t[-s, --start_point]: Geojson file containing all the pair of points to calculate the shortest path between them."
        "\n\t[-e, --end_point]: Geojson file containing all the pair of points to calculate the shortest path between them."
        "\n\t[-o, --outputFolder]: The final destination where the output geojson and summary files will be located."
        "\n\t[-c, --cost]: The impedance/cost attribute to calculate the shortest path."
        "\n\t[-t, --transportMode]: The transport mode used to calculate the shortest path."
        "\n\t[--cost_only]: Only the cost summary should be calculated."
        "\n\t[--is_entry_list]: The start and end points entries are folders containing a list of geojson files."
        "\n\t[--all]: Calculate the shortest path to all the impedance/cost attributes."
        "\n\nImpedance/cost values allowed:"
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
    opts, args = getopt.getopt(
        argv, "s:e:o:c:t:",
        ["start_point=", "end_point=", "outputFolder=", "cost", "transportMode", "cost_only", "all", "help"]
    )

    startPointsGeojsonFilename = None
    outputFolder = None
    # impedance = CostAttributes.DISTANCE
    impedance = None
    car_impedances = {
        "DISTANCE": CostAttributes.DISTANCE,
        "SPEED_LIMIT_TIME": CostAttributes.SPEED_LIMIT_TIME,
        "DAY_AVG_DELAY_TIME": CostAttributes.DAY_AVG_DELAY_TIME,
        "MIDDAY_DELAY_TIME": CostAttributes.MIDDAY_DELAY_TIME,
        "RUSH_HOUR_DELAY": CostAttributes.RUSH_HOUR_DELAY

    }

    bicycle_impedances = {
        "DISTANCE": CostAttributes.DISTANCE,
        "BICYCLE_FAST_TIME": CostAttributes.BICYCLE_FAST_TIME,
        "BICYCLE_SLOW_TIME": CostAttributes.BICYCLE_SLOW_TIME

    }

    allImpedanceAttribute = False
    costOnly = False
    isEntryList = False

    impedanceErrorMessage = "Use the paramenter -c or --cost.\nValues allowed: DISTANCE, SPEED_LIMIT_TIME, DAY_AVG_DELAY_TIME, MIDDAY_DELAY_TIME, RUSH_HOUR_DELAY.\nThe parameter --all enable the analysis for all the impedance attributes."
    transportModeErrorMessage = "Use the paramenter -t or --transportMode.\nValues allowed: PRIVATE_CAR, BICYCLE."

    for opt, arg in opts:
        if opt in "--help":
            printHelp()
            return

        print("options: %s, arg: %s" % (opt, arg))

        if opt in ("-s", "--start_point"):
            startPointsGeojsonFilename = arg

        if opt in ("-e", "--end_point"):
            endPointsGeojsonFilename = arg

        if opt in ("-o", "--outputFolder"):
            outputFolder = arg

        if opt in ("-t", "--transportMode"):
            transportModeSelected = arg

        if opt in "--cost_only":
            costOnly = True

        if opt in "--is_entry_list":
            isEntryList = True

        if opt in "--all":
            allImpedanceAttribute = True
        else:
            if opt in ("-c", "--cost"):
                if (arg not in car_impedances) and (arg not in bicycle_impedances):
                    raise ImpedanceAttributeNotDefinedException(
                        impedanceErrorMessage)

                if arg in car_impedances:
                    impedance = car_impedances[arg]
                elif arg in bicycle_impedances:
                    impedance = bicycle_impedances[arg]

    if not startPointsGeojsonFilename or not endPointsGeojsonFilename or not outputFolder:
        raise NotParameterGivenException("Type --help for more information.")

    if not transportModeSelected:
        raise TransportModeNotDefinedException(
            transportModeErrorMessage)

    if not allImpedanceAttribute and not impedance:
        raise ImpedanceAttributeNotDefinedException(
            impedanceErrorMessage)

    postgisServiceProvider = PostgisServiceProvider()

    transportMode = None
    impedances = None

    if transportModeSelected == TransportModes.BICYCLE:
        transportMode = BicycleTransportMode(postgisServiceProvider)
        impedances = bicycle_impedances
    elif transportModeSelected == TransportModes.PRIVATE_CAR:
        transportMode = PrivateCarTransportMode(postgisServiceProvider)
        impedances = car_impedances

    starter = MetropAccessDigiroadApplication(
        transportMode=transportMode
    )

    if not isEntryList:
        prefix = ""
        executeSpatialDataAnalysis(outputFolder, startPointsGeojsonFilename, endPointsGeojsonFilename,
                                   starter,
                                   impedance, impedances, allImpedanceAttribute,
                                   costOnly,
                                   prefix)
    else:
        for startRoot, startDirs, startFiles in os.walk(startPointsGeojsonFilename):
            for startPointsFilename in startFiles:
                if startPointsFilename.endswith("geojson"):

                    for endRoot, endDirs, endFiles in os.walk(endPointsGeojsonFilename):
                        for endPointsFilename in endFiles:
                            if endPointsFilename.endswith("geojson"):

                                executeSpatialDataAnalysis(outputFolder,
                                                           os.path.join(startRoot, startPointsFilename),
                                                           os.path.join(endRoot, endPointsFilename),
                                                           starter,
                                                           impedance, impedances, allImpedanceAttribute,
                                                           costOnly,
                                                           startPointsFilename + "_" + endPointsFilename + "-")


def executeSpatialDataAnalysis(outputFolder, startPointsGeojsonFilename, endPointsGeojsonFilename,
                               starterApplication,
                               impedance, impedances, allImpedanceAttribute,
                               costOnly,
                               prefix):
    Logger.configureLogger(outputFolder, prefix)
    config = getConfigurationProperties()
    # wfsServiceProvider = WFSServiceProvider(
    #     wfs_url=config["wfs_url"],
    #     nearestVertexTypeName=config["nearestVertexTypeName"],
    #     nearestCarRoutingVertexTypeName=config["nearestCarRoutingVertexTypeName"],
    #     shortestPathTypeName=config["shortestPathTypeName"],
    #     outputFormat=config["outputFormat"]
    # )

    if impedance and not allImpedanceAttribute:
        if not costOnly:
            starterApplication.calculateTotalTimeTravel(
                startCoordinatesGeojsonFilename=startPointsGeojsonFilename,
                endCoordinatesGeojsonFilename=endPointsGeojsonFilename,
                outputFolderPath=outputFolder,
                costAttribute=impedance
            )
            starterApplication.createDetailedSummary(
                folderPath=outputFolder,
                costAttribute=impedance,
                outputFilename=prefix + "metroAccessDigiroadSummary.geojson"
            )

        starterApplication.createGeneralSummary(
            startCoordinatesGeojsonFilename=startPointsGeojsonFilename,
            endCoordinatesGeojsonFilename=endPointsGeojsonFilename,
            costAttribute=impedance,
            outputFolderPath=outputFolder,
            outputFilename=prefix + "dijsktraCostMetroAccessDigiroadSummary.geojson"
        )

    if allImpedanceAttribute:
        if not costOnly:
            starterApplication.calculateTotalTimeTravel(
                startCoordinatesGeojsonFilename=startPointsGeojsonFilename,
                endCoordinatesGeojsonFilename=endPointsGeojsonFilename,
                outputFolderPath=outputFolder,
                costAttribute=impedances
            )

        for key in impedances:
            if not costOnly:
                starterApplication.createDetailedSummary(
                    folderPath=outputFolder,
                    costAttribute=impedances[key],
                    outputFilename=prefix + "metroAccessDigiroadSummary.geojson"
                )
            starterApplication.createGeneralSummary(
                startCoordinatesGeojsonFilename=startPointsGeojsonFilename,
                endCoordinatesGeojsonFilename=endPointsGeojsonFilename,
                costAttribute=impedances[key],
                outputFolderPath=outputFolder,
                outputFilename=prefix + "dijsktraCostMetroAccessDigiroadSummary.geojson"
            )
