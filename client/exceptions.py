# Defines the custom exception classes

class Error(Exception):

    def __init__(self, message=''):
        super(Error, self).__init__("Error occured" + message)

class PackageNotFoundException(Exception):
    def __init__(self, location):
        super(PackageNotFoundException, self).__init__(
            "Package could not be found at the "
            "specific location: %s" % location)

class TimeOutException(Error):
    def __init__(self):
        message = "Timeout occurred during operation"
        super(TimeOutException, self).__init__(message)

class ConfigFileNotPresentException(Error):
    def __init__(self, location):
        message = "Configuration file is not present in %s" % location
        super(ConfigFileNotPresentException, self).__init__(message)

class PackageChecksumMismatch(Error):
    def __init__(self):
        message = "Package file checksum mismatched"
        super(PackageChecksumMismatch, self).__init__(message)

class VersionNotApplicable(Error):
    def __init__(self):
        message = "Package is not built for the current Pi's version"
        super(VersionNotApplicable, self).__init__(message)

class BackupDirCreationError(Error):
    def __init__(self, message):
        super(BackupDirCreationError, self).__init__(message)

class BackupDirDeletionError(Error):
    def __init__(self, message):
        super(BackupDirDeletionError, self).__init__(message)
