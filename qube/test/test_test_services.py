#!/usr/bin/python
"""
Add docstring here
"""
import os
import time
import unittest

import mock
from mock import patch
import mongomock


with patch('pymongo.mongo_client.MongoClient', new=mongomock.MongoClient):
    os.environ['TEST_MONGOALCHEMY_CONNECTION_STRING'] = ''
    os.environ['TEST_MONGOALCHEMY_SERVER'] = ''
    os.environ['TEST_MONGOALCHEMY_PORT'] = ''
    os.environ['TEST_MONGOALCHEMY_DATABASE'] = ''

    from qube.src.models.test import Test
    from qube.src.services.testservice import TestService
    from qube.src.commons.context import AuthContext
    from qube.src.commons.error import ErrorCodes, TestServiceError


class TestTestService(unittest.TestCase):
    @mock.patch('pymongo.mongo_client.MongoClient', new=mongomock.MongoClient)
    def setUp(self):
        context = AuthContext("23432523452345", "tenantname",
                              "987656789765670", "orgname", "1009009009988",
                              "username", False)
        self.testService = TestService(context)
        self.test_api_model = self.createTestModelData()
        self.test_data = self.setupDatabaseRecords(self.test_api_model)
        self.test_someoneelses = \
            self.setupDatabaseRecords(self.test_api_model)
        self.test_someoneelses.tenantId = "123432523452345"
        with patch('mongomock.write_concern.WriteConcern.__init__',
                   return_value=None):
            self.test_someoneelses.save()
        self.test_api_model_put_description \
            = self.createTestModelDataDescription()
        self.test_data_collection = [self.test_data]

    def tearDown(self):
        with patch('mongomock.write_concern.WriteConcern.__init__',
                   return_value=None):
            for item in self.test_data_collection:
                item.remove()
            self.test_data.remove()

    def createTestModelData(self):
        return {'name': 'test123123124'}

    def createTestModelDataDescription(self):
        return {'description': 'test123123124'}

    @mock.patch('pymongo.mongo_client.MongoClient', new=mongomock.MongoClient)
    def setupDatabaseRecords(self, test_api_model):
        with patch('mongomock.write_concern.WriteConcern.__init__',
                   return_value=None):
            test_data = Test(name='test_record')
            for key in test_api_model:
                test_data.__setattr__(key, test_api_model[key])

            test_data.description = 'my short description'
            test_data.tenantId = "23432523452345"
            test_data.orgId = "987656789765670"
            test_data.createdBy = "1009009009988"
            test_data.modifiedBy = "1009009009988"
            test_data.createDate = str(int(time.time()))
            test_data.modifiedDate = str(int(time.time()))
            test_data.save()
            return test_data

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_post_test(self, *args, **kwargs):
        result = self.testService.save(self.test_api_model)
        self.assertTrue(result['id'] is not None)
        self.assertTrue(result['name'] == self.test_api_model['name'])
        Test.query.get(result['id']).remove()

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_put_test(self, *args, **kwargs):
        self.test_api_model['name'] = 'modified for put'
        id_to_find = str(self.test_data.mongo_id)
        result = self.testService.update(
            self.test_api_model, id_to_find)
        self.assertTrue(result['id'] == str(id_to_find))
        self.assertTrue(result['name'] == self.test_api_model['name'])

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_put_test_description(self, *args, **kwargs):
        self.test_api_model_put_description['description'] =\
            'modified for put'
        id_to_find = str(self.test_data.mongo_id)
        result = self.testService.update(
            self.test_api_model_put_description, id_to_find)
        self.assertTrue(result['id'] == str(id_to_find))
        self.assertTrue(result['description'] ==
                        self.test_api_model_put_description['description'])

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_get_test_item(self, *args, **kwargs):
        id_to_find = str(self.test_data.mongo_id)
        result = self.testService.find_by_id(id_to_find)
        self.assertTrue(result['id'] == str(id_to_find))

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_get_test_item_invalid(self, *args, **kwargs):
        id_to_find = '123notexist'
        with self.assertRaises(TestServiceError):
            self.testService.find_by_id(id_to_find)

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_get_test_list(self, *args, **kwargs):
        result_collection = self.testService.get_all()
        self.assertTrue(len(result_collection) == 1,
                        "Expected result 1 but got {} ".
                        format(str(len(result_collection))))
        self.assertTrue(result_collection[0]['id'] ==
                        str(self.test_data.mongo_id))

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_delete_toolchain_not_system_user(self, *args, **kwargs):
        id_to_delete = str(self.test_data.mongo_id)
        with self.assertRaises(TestServiceError) as ex:
            self.testService.delete(id_to_delete)
        self.assertEquals(ex.exception.errors, ErrorCodes.NOT_ALLOWED)

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_delete_toolchain_by_system_user(self, *args, **kwargs):
        id_to_delete = str(self.test_data.mongo_id)
        self.testService.auth_context.is_system_user = True
        self.testService.delete(id_to_delete)
        with self.assertRaises(TestServiceError) as ex:
            self.testService.find_by_id(id_to_delete)
        self.assertEquals(ex.exception.errors, ErrorCodes.NOT_FOUND)
        self.testService.auth_context.is_system_user = False

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    def test_delete_toolchain_item_someoneelse(self, *args, **kwargs):
        id_to_delete = str(self.test_someoneelses.mongo_id)
        with self.assertRaises(TestServiceError):
            self.testService.delete(id_to_delete)
