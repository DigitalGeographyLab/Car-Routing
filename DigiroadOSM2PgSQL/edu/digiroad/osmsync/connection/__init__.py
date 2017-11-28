import shutil
import subprocess

import requests
# from DigiroadOSM2PgSQL.edu.digiroadExceptions import NotOSMURLGivenException, NotPathException
# from DigiroadOSM2PgSQL.edu.enumerations import OsmosisCommands
from edu.digiroad.digiroadExceptions import NotOSMURLGivenException, NotPathException
from edu.digiroad.enumerations import OsmosisCommands


class DigiroadOSMConnection:
    def download(self, osmURL=None, outputPath=None):
        """
        Download a OSM/PBF file from the given URL and store the file in the outputPath selected.

        :param osmURL:
        :param outputPath:
        :return:
        """
        if not osmURL or (not osmURL.endswith(".osm") and not osmURL.endswith(".pbf")):
            raise NotOSMURLGivenException()

        if not outputPath:
            raise NotPathException()

        # Taken from https://stackoverflow.com/questions/16694907/how-to-download-large-file-in-python-with-requests-py
        local_filename = osmURL.split('/')[-1]
        r = requests.get(osmURL, stream=True)
        filename = outputPath + local_filename
        with open(filename, 'wb') as f:
            shutil.copyfileobj(r.raw, f)

        return filename
        # End

    def uploadOSMFile2PgSQLDatabase(self, username, password, databaseName, styleURL, inputFile,
                                    fileFormat=OsmosisCommands.PBF):
        """
        Use the osm2pgsql tool to upload the data from the OSM/PBF file to a posgreSQL database.

        :param username:
        :param password:
        :param databaseName:
        :param styleURL:
        :param inputFile:
        :param fileFormat:
        :return:
        """
        if not inputFile:
            raise NotOSMURLGivenException()

        # command = 'osm2pgsql -c -d osm_test --username postgres --password --slim -C 4000 -S "%s" "%w" -r pbf -C 6000' % (
        #     styleURL, outputFile)

        # format = outputFile.split(".")[-1]# "pbf"
        # if format == "osm":
        #     format == "xml"

        split_command = ["osm2pgsql", "-c", '-d', databaseName, "--username", username,
                         "--password",
                         "-C",
                         "4000",
                         "--slim",
                         "-S", styleURL, inputFile, "-r", fileFormat, "-C", "6000"
                         ]

        try:
            p = subprocess.Popen(split_command,
                                 # shell=True,
                                 stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)

            p.stdin.write(b'%s\n' % password)
            p.stdin.flush()

            (output, err) = p.communicate()

            # if err:
            #     raise BaseException(err)
            # This makes the wait possible
            p_status = p.wait()

            print("uploadOSMFile2PgSQLDatabase command output: %s" % output)

        except Exception as err:  # traceback.print_exc(file=sys.stdout)
            raise err

        completed = True
        return completed

    def imposmFile2PgSQLDatabase(self, username, password, databaseName, inputFile, mappingFile, hostname, port):
        """
        Use the osm2pgsql tool to upload the data from the OSM/PBF file to a posgreSQL database.

        :param username:
        :param password:
        :param databaseName:
        :param styleURL:
        :param inputFile:
        :param fileFormat:
        :return:
        """
        if not inputFile:
            raise NotOSMURLGivenException()

        # command = 'osm2pgsql -c -d osm_test --username postgres --password --slim -C 4000 -S "%s" "%w" -r pbf -C 6000' % (
        #     styleURL, outputFile)

        # format = outputFile.split(".")[-1]# "pbf"
        # if format == "osm":
        #     format == "xml"

        split_command = [
            "/opt/codes/imposm3/./imposm3",
            "import",
            "-connection",
            "postgis://%s:%s@%s:%s/%s" % (
                username, password, hostname, port, databaseName),
            "-mapping", mappingFile,
            "-read", inputFile,
            "-write",
            "-overwritecache",
            "-deployproduction"
        ]

        try:
            p = subprocess.Popen(split_command,
                                 # shell=True,
                                 stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)

            # p.stdin.write(b'%s\n' % password)
            # p.stdin.flush()

            (output, err) = p.communicate()

            # if err:
            #     raise BaseException(err)
            # This makes the wait possible
            p_status = p.wait()

            print("uploadOSMFile2PgSQLDatabase command output: %s" % output)

        except Exception as err:  # traceback.print_exc(file=sys.stdout)
            raise err

        completed = True
        return completed
