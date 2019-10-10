# Daemon code from  "A simple unix/linux daemon in Python" by Sander Marechal
# and Joseph Ernest, 2016/11/12

# Third Party Libraries
import atexit
import os
from signal import signal, SIGTERM
import sys
import time

# Code files
import constants
import download_package
import update_system
import utils


class Daemon(object):
    """
    A generic daemon class.

    Usage: subclass the Daemon class and override the run() method
    """
    def __init__(self, pidfile='_.pid', stdin='/dev/null',
                 stdout='/dev/null', stderr='/dev/null'):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile

    def daemonize(self):
        """
        do the UNIX double-fork magic, see Stevens' "Advanced
        Programming in the UNIX Environment" for details (ISBN 0201563177)
        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
        """
        try:
            print("Starting daemon")
            pid = os.fork()
            if pid > 0:
                # exit first parent
                sys.exit(0)
        except OSError, e:
            sys.stderr.write("fork #1 failed: %d (%s)\n" %
                             (e.errno, e.strerror))
            sys.exit(1)
        # decouple from parent environment
        os.setsid()
        os.umask(0)
        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # exit from second parent
                sys.exit(0)
        except OSError, e:
            sys.stderr.write("fork #2 failed: %d (%s)\n" %
                             (e.errno, e.strerror))
            sys.exit(1)
        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = file(self.stdin, 'r')
        so = file(self.stdout, 'a+')
        se = file(self.stderr, 'a+', 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        atexit.register(self.onstop)
        signal(SIGTERM, lambda signum, stack_frame: exit())

        # write pidfile
        pid = str(os.getpid())
        file(self.pidfile, 'w+').write("%s\n" % pid)

    def onstop(self):
        self.quit()
        os.remove(self.pidfile)

    def start(self):
        """
        Start the daemon
        """
        # Check for a pidfile to see if the daemon already runs
        try:
            pf = file(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if pid:
            message = "pidfile %s already exist. Daemon already running?\n"
            sys.stderr.write(message % self.pidfile)
            sys.exit(1)
        # Start the daemon
        self.daemonize()
        self.run()

    def stop(self):
        """
        Stop the daemon
        """
        # Get the pid from the pidfile
        try:
            pf = file(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if not pid:
            message = "pidfile %s does not exist. Daemon not running?\n"
            sys.stderr.write(message % self.pidfile)
            return  # not an error in a restart

        # Try killing the daemon process
        try:
            while 1:
                os.kill(pid, SIGTERM)
                time.sleep(0.1)
        except OSError, err:
            err = str(err)
            if err.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print str(err)
                sys.exit(1)

    def restart(self):
        """
        Restart the daemon
        """
        self.stop()
        self.start()

    def run(self):
        """
        You should override this method when you subclass Daemon.
        It will be called after the process has been
        daemonized by start() or restart().
        """

    def quit(self):
        """
        You should override this method when you subclass Daemon.
        It will be called before the process is stopped.
        """


class UpdaterDaemon(Daemon):

    def __init__(self):
        super(UpdaterDaemon, self).__init__()
        self.downloader = download_package.PackageDownloader()
        self.updater = update_system.Updater()

    def run(self):
        # If any of the Update folders dont exist, then create them
        for dirc in constants.DIRLIST:
            if not os.path.exists(dirc):
                os.mkdir(dirc)

        while True:
            status, attr1, attr2, attr3 = utils.readMarkerFile()
            # ToDo: This might fail if 4 values are written during Download
            if status == constants.READY:
                location = self.check_for_package()
                if location:
                    if not downloader.startDownload(location):
                        print("Download failed")
                        utils.deleteDownloadedPackage()
                    else:
                        print("Download completed")

                else:
                    time.sleep(constants.DAEMON_SLEEP_TIME)
                    continue
            elif status == constants.DOWNLOAD:
                location = utils.checkPackage(utils.getPiVersion())
                # The Assumption here is that there would only be one new
                # release package. If a Pi is OFF for a long time, it wont
                # be able to download multiple packages and update all of
                # them , atleast not right now.
                if attr == constants.PARTIAL:
                    print("Downloading package from last point")
                    if downloader.startIncrementalDownload(location):
                        print(status, " completed")
                    else:
                        print("Download failed")
                        utils.deleteDownloadedPackage()

                elif attr == constants.FULL:
                    print("Downloading package again")
                    downloader.startFullDownload(location)
                    print(status, " completed")
            elif status == constants.UPDATE or status == constants.ROLLBACK:
                if attr == constants.REBOOT:
                    print(status, " completed")
                    utils.deleteDownloadedPkg()
                elif attr == constants.IN_PROGRESS:
                    # Start Rollback irrespective of the last failure point
                    self.updater.rollback()
            elif status == constants.DOWNLOAD_COMPLETED:
                # Update should happen only after Pi boots up again
                self.updater.update()
            elif status == constants.NO_MARKER_FILE:
                continue
            else:
                print("Marker file corrupted")
                utils.removeMarkerFile()

        def check_for_package(self):
            if not utils.isDeviceAuthenticated(utils.getDeviceId()):
                print("Device is not authenticated")
                return
            else:
                return utils.checkPackage(utils.getPiVersion())

if __name__ == '__main__':
    d = UpdaterDaemon()
    d.run()
