#!/usr/bin/python
"""
Add docstring here
"""
import time
import unittest

import mock

from mock import patch
import mongomock


class TestTestModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("before class")

    @mock.patch('pymongo.mongo_client.MongoClient', new=mongomock.MongoClient)
    def test_create_test_model(self):
        from qube.src.models.test import Test
        test_data = Test(name='testname')
        test_data.tenantId = "23432523452345"
        test_data.orgId = "987656789765670"
        test_data.createdBy = "1009009009988"
        test_data.modifiedBy = "1009009009988"
        test_data.createDate = str(int(time.time()))
        test_data.modifiedDate = str(int(time.time()))
        with patch('mongomock.write_concern.WriteConcern.__init__',
                   return_value=None):
            test_data.save()
            self.assertIsNotNone(test_data.mongo_id)
            test_data.remove()

    @classmethod
    def tearDownClass(cls):
        print("After class")


if __name__ == '__main__':
    unittest.main()
