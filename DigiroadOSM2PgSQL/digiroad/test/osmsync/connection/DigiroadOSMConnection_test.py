import os
import unittest

from digiroad.digiroadExceptions import NotOSMURLGivenException, NotPathException
from digiroad.enumerations import OsmosisCommands
from digiroad.osmsync.connection import DigiroadOSMConnection


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
        outputPath = self.dir + "%digiroad%test%data%".replace("%", os.sep)

        self.assertIsNotNone(self.osmConnection.download(osmURL=URL,
                                                         outputPath=outputPath))

    def test_givenNoneOSMFileURL_then_throwException(self):
        self.assertRaises(NotOSMURLGivenException, self.osmConnection.uploadOSMFile2PgSQLDatabase, None, None,
                          None, None, None, None)

    # @unittest.skip("Skipping to do not spend time uploading the data into the pg database")
    def test_givenOSMFileURL_then_uploadData2PgSQL(self):
        # pbfFile = self.dir + "%edu%test%data%sample_osmosis.osm.pbf"
        pbfFile = self.dir + "%digiroad%test%data%sub-region-of-finland-latest.osm.pbf".replace("%", os.sep)
        styleURL = self.dir + "%digiroad%test%data%default.style".replace("%", os.sep)

        self.assertEqual(True, self.osmConnection.uploadOSMFile2PgSQLDatabase(username="postgres", password="hmaa",
                                                                              databaseName="osm_helsinki",
                                                                              styleURL=styleURL, inputFile=pbfFile,
                                                                              fileFormat=OsmosisCommands.PBF))
