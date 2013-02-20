import unittest, mock
import Uforia, os

@mock.patch('config.DEBUG', False)
class TestDbworker(unittest.TestCase):
    def setUp(self):
        self.db = mock.Mock()

        self.sentinel = ('No more tasks','','','')
        self.testdata = [
            ('test1', 1, ('column1', 'column2'), ('abc', 'xyz')),
            ('test2', 2, ('column1', 'column2'), ('123', '456')),
            self.sentinel
        ]

    def testDbworkerStopsWithNoTasks(self):
        dbqueue = mock.Mock()
        dbqueue.get.return_value = self.sentinel

        Uforia.dbworker(dbqueue, self.db)

        self.assertTrue(dbqueue.task_done.called, "dbqueue task must be set as done")

    def testDbWorkerDoesNotStoreWithNoTasks(self):
        dbqueue = mock.Mock()
        dbqueue.get.return_value = self.sentinel

        Uforia.dbworker(dbqueue, self.db)

        self.assertFalse(self.db.store.called, "db.store was called while sentinel value was sent")

    def testDbworkerStoresDataCorrectly(self):
        dbqueue = mock.Mock()

        # side_effect allows us to return a different value each time
        # the method is called
        dbqueue.get.side_effect = self.testdata

        Uforia.dbworker(dbqueue, self.db)

        expected = [
            mock.call(*self.testdata[0]),
            mock.call(*self.testdata[1])
        ]

        self.assertTrue(self.db.store.call_args_list == expected, "data was not written correctly or in the same order")

    def testDbworkerClosesConnection(self):
        dbqueue = mock.Mock()
        dbqueue.get.side_effect = self.testdata

        Uforia.dbworker(dbqueue, self.db)

        self.assertTrue(self.db.connection.close.called, "database connection was not closed")

@mock.patch('config.DEBUG', False)
class TestFileScanner(unittest.TestCase):
    def setUp(self):
        self.testDir = [ ('/TESTDATA', [], [ 'test.txt', 'loreen-euphoria.mp3' ]), ]

        self.osWalkPatcher = mock.patch('os.walk')
        self.MockOsWalk = self.osWalkPatcher.start()
        self.MockOsWalk.return_value = iter(self.testDir)

        self.consumers = mock.Mock()

    def tearDown(self):
        self.osWalkPatcher.stop()

    def testFileScannerClosesConsumers(self):
        Uforia.fileScanner(self.testDir[0], self.consumers, None, None)

        self.consumers.close.assert_called_once_with()

    def testFileScannerJoinsConsumers(self):
        Uforia.fileScanner(self.testDir[0], self.consumers, None, None)

        self.consumers.join.assert_called_once_with()

    def testFileScannerHandlesAllFiles(self):
        self.assertTrue(os.walk == self.MockOsWalk)
        Uforia.fileScanner(self.testDir[0], self.consumers, None, None)

        fullPaths = []
        for args, kwargs in self.consumers.apply_async.call_args_list:
            fullPaths.append(kwargs['args'][0][0])

        for i, fullPath in enumerate(fullPaths):
            self.assertTrue(fullPath.endswith(self.testDir[0][2][i]), "not all files have been processed")

    def testFileScannerHashIdsAreUnique(self):
        Uforia.fileScanner(self.testDir[0], self.consumers, None, None)

        hashIds = []
        for args, kwargs in self.consumers.apply_async.call_args_list:
            hashIds.append(kwargs['args'][0][1])

        self.assertTrue(len(hashIds) == len(set(hashIds)), "hash id contain duplicate values")

if __name__ == '__main__':
    unittest.main()