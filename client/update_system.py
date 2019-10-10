from collections import OrderedDict
import configparser
import constants
import exceptions
import glob
import subprocess
import utils


class ConfigurationParser(object):
    parser = configparser.ConfigParser()

    def verify_path(path=None):
        if not os.path.isfile(path):
            raise exceptions.ConfigFileNotPresentException(path)
        return True

    def read_file_for_backup(self):
        return self.read_file(constants.UPDATE_TMP_DIR + constants.UPDATE_INI,
                              section=constants.BACKUP)

    def read_file_for_metadata(self):
        return self.read_file(filename, section=constants.METADATA)

    def read_file(path=None, section=None):
        parser.read(path)
        kv_pair = OrderedDict()
        if section and section in parser._sections:
            for key in parser[section]:
                kv_pair[key] = parser[section][key]
        return kv_pair


class UpdateSystem(object):
    def __init__(self):
        self.__parser = ConfigurationParser()
        self.updateParser = constants.UPDATE_TMP_DIR + constants.UPDATE_INI
        self.reboot = False

    def setRebootStatus(self, reboot):
        self.reboot = reboot

    def __executeUpdate(self, pkgLoc):
        ''' This function is used to update the system

        # Read the INI File for all scripts from the pkgLoc
        # Execute the scripts in order of the mentions in the JSON file
        # update the Marker File with the information.
        # Once done, return status.
        # In case of multiple packages to be installed together, keep an option
        # Delete the package, call utils.deleteDownloadedPkg at the end
        '''
        scripts = self.__parser.read_file(self.updateParser, constants.SCRIPTS)
        execs = self.__parser.read_file(self.updateParser, constants.EXECS)
        drivers = self.__parser.read_file(self.updateParser, constants.DRIVERS)
        if drivers:
            for key, value in drivers.iteritems():
                print("Copy the file for %s" % key)
                name = value.split(" ")[0]
                path = value.split(" ")[1]
                utils.copyData(
                    src=constants.UPDATE_TMP_DIR + "/" + constants.DRIVERS,
                    dest=path)
        if execs:
            for key, value in execs.iteritems():
                print("Copy the file for %s" % key)
                name = value.split(" ")[0]
                path = value.split(" ")[1]
                utils.copyData(
                    src=constants.UPDATE_TMP_DIR + "/" + constants.EXECS,
                    dest=path)
        if scripts:
            for key, value in scripts.iteritems():
                print("Executing the script: %s" % key)
                script = value.split(" ")[0]
                user = value.split(" ")[1]
                utils.execScript(script, user)
        # Copy the backup file somewhere
        if self.reboot:
            utils.updateMarkerFile(constants.UPDATE, constants.REBOOT,
                                   None, None)
            utils.rebootSystem()
        else:
            print("Update completed")

class RollbackSystem(object):
    def __init__(self):
        self.__parser = ConfigurationParser()
        self.rollbackParser = constants.UPDATE_TMP_DIR + constants.ROLLBACK_INI
        self.reboot = False

    def setRebootStatus(self, reboot):
        self.reboot = reboot

    def __executeRollback(self, pkgLoc):
        # Read the Marker file for the total scripts completed
        # Read the INI file for rollback scripts
        # Go back to the last backup as per timestamp and recover the data
        # Once done, update Marker file with the status
        self.__parser.read_file(self.rollbackParser)
        scripts = self.__parser.read_file(self.rollbackParser,
                                          constants.SCRIPTS)
        if scripts:
            for key, value in scripts.iteritems():
                print("Executing the script: %s" % key)
                script = value.split(" ")[0]
                user = value.split(" ")[1]
                utils.execScript(script, user)
        if self.reboot:
            utils.updateMarkerFile(constants.UPDATE, constants.REBOOT,
                                   None, None)
            utils.rebootSystem()
        print("Rollback completed")


class Updater(object):
    # Extract Package to a specific location
    # Verify Metadata
    # Take Backup of the data as per timestamp
    # Start Update/Rollback
    def __init__(self):
        super(Updater, self).__init__()
        self.parser = ConfigurationParser()
        self.update = UpdateSystem()
        self.rollback = RollbackSystem()

    def rollback(self):
        self.initiate(constants.ROLLBACK)
        utils.updateMarkerFile(constants.ROLLBACK, constants.IN_PROGRESS,
                               None, None)
        self.rollback.__executeRollback(constants.UPDATE_TMP_DIR)

    def update(self):
        self.initiate(constants.UPDATE)
        utils.updateMarkerFile(constants.UPDATE, constants.IN_PROGRESS,
                               None, None)
        self.update.__executeUpdate(constants.UPDATE_TMP_DIR)

    def initiate(self, operation):
        loc = glob.glob(constants.DOWNLOAD_DIR + "/*.tar")
        if len(loc) > 1:
            raise Exception("Found more than one package")
        elif loc == []:
            raise Exception("No Package found")
        else:
            utils.extractTarFile(loc)

        if self.parser.verify_path(self.update.updateParser):
            self.__verifyMetaData(operation, self.update.updateParser)
            self.__initiateDataBackup()
        elif self.parser.verify_path(self.rollback.rollbackParser):
            self.__verifyMetaData(operation, self.rollback.rollbackParser)
        else:
            raise NoParserFoundException()

    def __verifyMetaData(self, operation, parserFile):
        metadata = self.parser.read_file_for_metadata(parserFile)
        if operation == constants.UPDATE and metadata[
                constants.CHECKSUM] != utils.getPackageChecksum():
            raise exceptions.PackageChecksumMismatch
        if utils.getPiVersion() not in metadata[constants.APP_VERSIONS]:
            raise exceptions.VersionNotApplicable
        self.update.setRebootStatus(
            metadata[constants.REBOOT]) if operation == constants.UPDATE \
            else self.rollbacksetRebootStatus(metadata[constants.REBOOT])

    def __initiateDataBackup(self):
        bkup_section = self.parser.read_file_for_backup()
        bkupDir = utils.createBackupDir()
        if bkup_section:
            for key, value in bkup_section.iteritems():
                print("Executing the script: %s" % key)
                script = value.split(" ")[0]
                path = value.split(" ")[1]
                utils.copyData(src=path + "/" + scripts,
                               dest=bkupDir)
                # Backup the data, then put it in a directory
