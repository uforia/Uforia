import unittest, mock
import Uforia

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
        self.assertFalse(self.db.store.called, "db.store was called while sentinel value was sent")
        self.assertTrue(self.db.connection.close.called, "database connection was not closed")

    def testDbworkerStoresDataCorrectly(self):
        dbqueue = mock.Mock()

        # side_effect allows us to return a different value each time
        # the method is called
        dbqueue.get.side_effect = self.testdata

        Uforia.dbworker(dbqueue, self.db)

        self.assertTrue(dbqueue.task_done.called, "dbqueue task must be set as done")

        expected = [
            mock.call(*self.testdata[0]),
            mock.call(*self.testdata[1])
        ]

        self.assertTrue(self.db.store.call_args_list == expected, "data was not written correctly or in the same order")

        self.assertTrue(dbqueue.task_done.called, "dbqueue task must be set as done")
        self.assertTrue(self.db.connection.commit.called, "changes were not committed to database")
        self.assertTrue(self.db.connection.close.called, "database connection was not closed")

if __name__ == '__main__':
    unittest.main()