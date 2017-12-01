import os
import subprocess

from digiroad.digiroadExceptions import NotOSMURLGivenException
from digiroad.enumerations import OsmosisCommands


class DigiroadOsmosis:
    def subRegionSplitter(self, osmFilePath=None, osmSubregionPath=None, left=0, right=0, top=0, bottom=0,
                          inputFormat=OsmosisCommands.PBF, outputFormat=OsmosisCommands.PBF):
        """
        Split the OSM/PBF file into the bounding box parametrized and store the new region in the osmSubregionPath.
        Only extract the hightway and railway tags.

        :param osmFilePath:
        :param osmSubregionPath:
        :param left:
        :param right:
        :param top:
        :param bottom:
        :param inputFormat:
        :param outputFormat:
        :return:
        """
        if not osmFilePath or not osmSubregionPath:
            raise NotOSMURLGivenException()

        local_filename = osmFilePath.split(os.sep)[-1]

        # command = 'osmosis --read-%s "%s" --tf accept-ways highway=* railway=* --used-node --bb left=%s right=%s top=%s bottom=%s --write-%s "%s"' % (
        #     inputFormat, osmFilePath, left, right, top, bottom, outputFormat, osmSubregionPath)

        output_filename = "%ssub-region-of-%s" % (osmSubregionPath, local_filename)
        split_command = [
            # "C:\HYapp\osmosis\\bin\osmosis.bat",
            "/opt/codes/osmosis/bin/osmosis",
            "--read-%s" % inputFormat,
            '%s' % osmFilePath,
            "--tf",
            "accept-ways",
            "highway=*",
            "railway=*",
            "--used-node",
            "--bb",
            "left=%s" % left, "right=%s" % right,
            "top=%s" % top, "bottom=%s" % bottom,
            "--write-%s" % outputFormat,
            output_filename
        ]

        try:
            print("Clipping %s in %s" % (osmFilePath, output_filename))

            # os.system(command)

            p = subprocess.Popen(split_command,
                                 # shell=True,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
            (output, err) = p.communicate()

            # This makes the wait possible
            p_status = p.wait()
            print(output)
            print("Clipped %s in %s" % (osmFilePath, output_filename))
        except Exception as err:
            # traceback.print_exc(file=sys.stdout)
            raise err

        return output_filename
