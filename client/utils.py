import constants
import datetime
import exceptions
import os
import requests
import shutil
import subprocess
import tarfile

def copyData(src=None, dest=None):
    try:
        if src and dest:
            shutil.copyfile(src, dest)
    except Exception as err:
        raise Exception("Failed to copy file to %s due to %s" %
                        (dest, err.message))

def execScript(name=None, user=None):
    try:
        os.system("sudo -u %s %s" % (
            user, constants.UPDATE_TMP_DIR + "/" +
            constants.SCRIPTS + "/" + name))
    except Exception as err:
        raise Exception("Failed to execute the script %s due to %s" %
                        (name, err.message))

def deleteDownloadedPkg():
    for file in glob.glob(constants.DOWNLOAD_DIR + "*.tar"):
        try:
            os.remove(file)
        except OSError:
            raise Exception("Error while deleting package")
    for object in glob.glob(constants.UPDATE_TMP_DIR + "*"):
        try:
            os.rmdir(folder)
        except OSError:
            try:
                os.remove(file)
            except OSError:
                raise Exception("Error while deleting the Temporary folder")

def extractTarFile(loc):
    try:
        pkg = tarfile.open(loc)
        pkg.extractall(path=constants.UPDATE_TMP_DIR)
        pkg.close()
    except Exception as err:
        raise Exception("Error while opening the tar package:%s" % err.message)

def fetchData(loc, start_range=None, end_range=None,
              cb_func=None):
    if not start_range and not end_range and cb_func:
        response = requests.get(loc)
        if response.status_code == 204:
            raise PackageNotFoundException(loc)
        elif response.status_code == 500:
            raise TimeOutException()
        cb_func()
        return
    else:
        # Code for Partial Download of the package
        # If return code is 204, raise PackageNotFoundError
        # Also need a Timeout error if status code is 500
        pass

def rebootSystem():
    os.system("/usr/sbin/shutdown -R now")

def isServerAccessible():
    return subprocess.call(
        ['ping', '-c', '1', '-W', '3', constants.SERVER_IP],
        stdout=open(os.devnull, 'w'), stderr=open(os.devnull, 'w'))
    # another alternative if ping is not supported
    # try:
    #     response = requests.head(constants.SERVER_IP)
    #     return True
    # except requests.exceptions.ConnectionError:
    #     return False

def getPiVersion():
    return open(constants.VERSION_FILE, "r").read()

def getDeviceId():
    return open(constants.DEVICE_ID_FILE, "r").read()
    # ToDo Need to get more information about how to retrieve Device ID

def isDeviceAuthenticated(deviceId):
    request = constants.SERVER_IP + constants.DEVICE_INFO + deviceId
    response = requests.post(request)  # ToDo: Need to check if response works?
    return True if response.text == "Authenticated" else False

def readMarkerFile():
    try:
        if os.path.isfile(constants.MARKER_FILE_LOC):
            markerFile = open(constants.MARKER_FILE_LOC, "r")
            data = markerFile.read()
            markerFile.close()
            return data.split(', ')
        else:
            return (constants.NO_MARKER_FILE,
                    None, None, None)
    except Exception as err:
        raise Exception("Unable to work on Marker file. Reason:%s" % err)

def updateMarkerFile(status, attr1=None, attr2=None, atr3=None):
    markerFile = open(constants.MARKER_FILE_LOC, "w+")
    fileData = "%s, %s, %s, %s" % (status, attr1, attr2, attr3)
    try:
        markerFile.write(fileData)
        return markerFile.close()
    except IOError as err:
        raise Exception(" Unable to write to Marker file:%s" % err)

def checkPackage(version):
    url = constants.SERVER_IP + constants.PACKAGE_API + "?version=" + version
    # ToDo: send HTTP request to the server on this URL.Server might not be
    # able to respond back unless we send a request to the server with
    # a ? in the get requests
    response = requests.get(url)
    if response.status_code == 204:
        return response.text
    else:
        print("No package found")
        return False
    # get the status back with the body, and it should have the complete
    # name of the package
    # This might need to be FTP since HTTP doesnt support this directly

def isPartialDownloadSupported():
    url = constants.SERVER_IP
    is_supported = False
    # Set the HEAD request, so that we can get the requisite information
    response = requests.head(url)
    length = constants.CONTENT_LENGTH
    if constants.ACCEPT_RANGES in response.headers.keys() and \
            response.headers[constants.ACCEPT_RANGES] == constants.BYTES:
        is_supported = True
    return (length, is_supported)

def removeMarkerFile():
    try:
        os.remove(constants.MARKER_FILE_LOC)
    except OSError:
        print("Seems like the marker file is already removed")

def createBackupDir():
    dirName = "bkup_" + (datetime.now()).strftime("%d%m%y_%h%m%s")
    try:
        path = constants.UPDATER_DIR + dirName
        os.mkdir(path)
        return path
    except OSError as err:
        raise exceptions.BackupDirCreationError(message=err.message)

def deleteBackupDir():
    try:
        for folder in glob.glob(constants.DOWNLOAD_DIR + "bkup_*"):
            shutil.rmtree(folder)
    except Exception as err:
        raise exceptions.BackupDirDeletionError(err.message)
