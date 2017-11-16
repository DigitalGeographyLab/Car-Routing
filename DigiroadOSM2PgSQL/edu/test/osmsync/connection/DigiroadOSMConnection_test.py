import os
import unittest

from edu.digiroad.digiroadExceptions import NotOSMURLGivenException, NotPathException
from edu.digiroad.enumerations import OsmosisCommands
from edu.digiroad.osmsync.connection import DigiroadOSMConnection


class DigiroadOSMConnectionTest(unittest.TestCase):
    def setUp(self):
        self.osmConnection = DigiroadOSMConnection()
        self.dir = os.getcwd()

    def test_givenEmptyURL_then_ThrowException(self):
        self.assertRaises(NotOSMURLGivenException, self.osmConnection.download, None, None)

    def test_givenNoneOSMFileURL_then_ThrowException(self):
        self.assertRaises(NotOSMURLGivenException, self.osmConnection.download, ".txt", None)

    def test_givenNoneOutputPath_then_ThrowException(self):
        self.assertRaises(NotPathException, self.osmConnection.download, ".osm", None)

    # @unittest.skip("Skipping to do not spend time downloading the file")
    def test_givenOSMFileURL_then_downloadOSMFile(self):
        URL = "http://download.geofabrik.de/europe/finland-latest.osm.pbf"
        outputPath = self.dir + "/edu/test/data/"

        self.assertIsNotNone(self.osmConnection.download(osmURL=URL,
                                                         outputPath=outputPath))

    def test_givenNoneOSMFileURL_then_throwException(self):
        self.assertRaises(NotOSMURLGivenException, self.osmConnection.uploadOSMFile2PgSQLDatabase, None, None,
                          None, None, None, None)

    # @unittest.skip("")
    def test_givenOSMFileURL_then_uploadData2PgSQL(self):
        # pbfFile = "C:\Users\jeisonle\Documents\Digital Geography Lab\Osmosis temp\sample_osmosis.osm.pbf"
        # styleURL = "C:\Users\jeisonle\Documents\Digital Geography Lab\Osmosis temp\default.style"

        pbfFile = self.dir + "/edu/test/data/sample_osmosis.osm.pbf"
        styleURL = self.dir + "/edu/test/data/default.style"

        self.assertEqual(True, self.osmConnection.uploadOSMFile2PgSQLDatabase(username="postgres", password="hmaa",
                                                                              databaseName="osm_test",
                                                                              styleURL=styleURL, inputFile=pbfFile,
                                                                              fileFormat=OsmosisCommands.PBF))
