import mock
import unittest
import updater.client.download_package as downloader

class TestPackageDownloader(unittest.TestCase):
    def setUp(self):
        self.dwnPkg = downloader.PackageDownloader()

    def testStartDownloadFailure(self):
        self.assertFalse(self.dwnPkg.startDownload(mock.Mock()))

if __name__ == '__main__':
    unittest.main()
