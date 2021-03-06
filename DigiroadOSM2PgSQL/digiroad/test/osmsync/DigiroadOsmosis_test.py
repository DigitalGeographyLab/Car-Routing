import os
import unittest

from digiroad.digiroadExceptions import NotOSMURLGivenException
from digiroad.osmsync import DigiroadOsmosis


class DigiroadOsmosisTest(unittest.TestCase):
    def setUp(self):
        self.digiroadOsmosis = DigiroadOsmosis()
        self.dir = os.getcwd()

    def test_givenEmptyURL_then_throwException(self):
        self.assertRaises(NotOSMURLGivenException, self.digiroadOsmosis.subRegionSplitter, None, None)

    # @unittest.skip("Skipping to do not spend time splitting the feature")
    def test_givenOSMURL_then_splitToTheSubRegion(self):
        pbfInputFile = self.dir + "%digiroad%test%data%finland-latest.osm.pbf".replace("%", os.sep)
        pbfOutputFile = self.dir + "%digiroad%test%data%".replace("%", os.sep)

        outputfile = self.digiroadOsmosis.subRegionSplitter(osmFilePath=pbfInputFile,
                                                            osmSubregionPath=pbfOutputFile,
                                                            left=24.59,
                                                            right=25.24,
                                                            top=60.35,
                                                            bottom=60.11)
        self.assertIsNotNone(self.checkFile(outputfile))

    def checkFile(self, pbfOutputFile):
        with open(pbfOutputFile, 'r') as f:
            return f
