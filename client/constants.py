# Constants defining file and folder locations
# Since UPDATER_DIR is used by others, need to define it before other constants
DEVICE_ID_FILE = "/home/pi/usrFiles/getCpuId.txt"
UPDATER_DIR = "/home/pi/updater/"
DOWNLOAD_DIR = UPDATER_DIR + "download/"
MARKER_FILE_LOC = UPDATER_DIR + "marker_file"
ROLLBACK_INI = "/rollback.ini"
UPDATE_INI = "/update.ini"
UPDATE_TMP_DIR = UPDATER_DIR + "tmp/"
VERSION_FILE = "/home/pi/usrFiles/ImageVerNo.txt"
DIRLIST = [UPDATER_DIR, DOWNLOAD_DIR, UPDATE_TMP_DIR]

# Daemon Constants
DAEMON_SLEEP_TIME = 86400  # 60*60*24

# Constants defining the Server constants
SERVER_IP = SERVER_URL = "https://127.0.0.1/"  # Can be moved to a config file
# SERVER MUST BE ACCESED WITH HTTPS
PACKAGE_API = "/packages/"
DEVICE_INFO = "device_info"  # URL where device information would be kept

# Constants for HTTP Packets
ACCEPT_RANGES = 'accept-ranges'
BYTES = 'bytes'
CONTENT_LENGTH = 'content-length'

# Constants for Update process
READY = "ready"
DOWNLOAD = "download"
DOWNLOAD_COMPLETED = "download_completed"
IN_PROGRESS = "progress"
PARTIAL = "partial"
FULL = "full"
UPDATE = "update"
ROLLBACK = "rollback"
REBOOT = "reboot"
METADATA = "metadata"
BACKUP = "backup"
SCRIPTS = "scripts"
EXECS = "executables"
DRIVERS = "drivers"
CHECKSUM = "checksum"
APP_VERSIONS = "applicable_versions"
NO_MARKER_FILE = "no_marker_file"
