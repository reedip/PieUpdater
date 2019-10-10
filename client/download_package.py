# Licensed under the Apache License, Version 2.0 (the "License")
import constants
import utils
import exceptions

class PackageDownloader(object):

    def __init__(self):
        packageSize = 0
        partialDownload = False
        byteSize = 1024

    def startDownload(self, package_loc):
        ''' This function is used to start the download of the pkg

        Input: Package Location from the server
        Output: Success/Failure of the package download
        '''
        try:
            self.packageSize, self.partialDownload = \
                utils.isPartialDownloadSupported()
            if self.packageSize:
                if self.partialDownload:
                    self.startIncrementalDownload(package_loc)
                else:
                    self.startFullDownload(package_loc)
            else:
                raise Exception("Package Size is ZERO!!!")
        except exceptions.PackageNotFoundException:
            print("Package could not be found in the server at"
                  "location %s" % package_loc)
            return False
        except Exception as e:
            print(" Fatal Exception occurred here " + str(e.message))
            return False

    def startIncrementalDownload(self, location):
        ''' This function is used for Downloading the file in increments

        This function can be called by the Download process or the Daemon,
        to ensure that partial download can work in case Pi reboots.
        In case the network breaks in between, the network will be tested
        after every 90 sec.
        The Marker file would be updated after every increment, so that if
        the Pi reboots, it can start from the last known byte.
        One situation can occur where in the Pi fails just after download
        and before updating the file, then the last byte would be downloaded
        again.
        Input: Location of the package
        Output: None
        '''
        status, downloadType, packageSize, readBytes = utils.readMarkerFile()
        if status == constants.READY:
            utils.updateMarkerFile(constants.DOWNLOAD,
                                   constants.PARTIAL, self.packageSize, "0")
        try:
            readBytes = int(readBytes)
            packageSize = int(packageSize)
        except ValueError:
            print("Marker File is not consistent")
        while status == constants.DOWNLOAD:
            try:
                for pkt in range(readBytes / byteSize,
                                 self.packageSize / self.byteSize):
                    end_bytes = readBytes + (pkt * byteSize)
                    if end_bytes > self.packageSize:
                        # Possible when packageSize is not a multe of byteSize
                        end_bytes = self.packageSize - (
                            readBytes + byteSize * (pkt - 1))
                    utils.fetchData(location, start_range=readBytes,
                                    end_range=end_bytes)
                    utils.updateMarkerFile(constants.DOWNLOAD,
                                           self.packageSize,
                                           end_bytes, constants.PARTIAL)
                status = CONSTANTS.READY
                self.setMarkerToDownloadCompleted()
            except exceptions.TimeOutException:
                while not utils.isServerAccessible():
                    time.sleep(90)

    def startFullDownload(self, location):
        status, downloadType, packageSize, readBytes = utils.readMarkerFile()
        if status == constants.READY:
            utils.updateMarkerFile(constants.DOWNLOAD)
        utils.fetchData(location, cb=self.setMarkerToReady)
        # This function is async in nature
        utils.updateMarkerFile(constants.DOWNLOAD_COMPLETE, None, None,
                               constants.FULL)
        # Think about adding a timeout option here as well?

    def setMarkerToDownloadCompleted(self):
        # This is used as a callback function. Once the data is downloaded
        # this function is called to set Marker File back to Ready
        utils.updateMarkerFile(constants.DOWNLOAD_COMPLETED)
