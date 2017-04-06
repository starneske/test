#!/usr/bin/python
"""
Add docstring here
"""
import io
import json
import os
import time
import unittest

from mock import patch
import mongomock

from qube.src.commons.utils import clean_nonserializable_attributes

# noinspection PyUnresolvedReferences
HELLO_WITH_ID = "/v1/test/{}"
HELLO = "/v1/test"
with patch('pymongo.mongo_client.MongoClient', new=mongomock.MongoClient):
    os.environ['TEST_MONGOALCHEMY_CONNECTION_STRING'] = ''
    os.environ['TEST_MONGOALCHEMY_SERVER'] = ''
    os.environ['TEST_MONGOALCHEMY_PORT'] = ''
    os.environ['TEST_MONGOALCHEMY_DATABASE'] = ''
    from qube.src.api.app import app
    from qube.src.models.test import Test


def auth_response():
    userinfo = {
        'id': '1009009009988',
        'type': 'org',
        'tenant': {
            'id': '23432523452345',
            'name': 'tenantname',
            'orgs': [{
                'id': '987656789765670',
                'name': 'orgname'
            }]
        },
        'is_system_user': False
    }
    return json.dumps(userinfo)


def system_user_auth_response():
    userinfo = {
        'id': '1009009009988',
        'type': 'org',
        'tenant': {
            'id': '23432523452345',
            'name': 'tenantname',
            'orgs': [{
                'id': '987656789765670',
                'name': 'orgname'

            }]
        },
        'is_system_user': True
    }
    return json.dumps(userinfo)


def invalid_auth_response():
    userinfo = {
        'id': '1009009009988',
        'type': 'master',
        'tenant': {
            'id': '23432523452345',
            'name': 'tenantname',
            'orgs': [{
                'id': '987656789765670',
                'name': 'orgname'
            }]
        },
        'is_system_user': False
    }
    return json.dumps(userinfo)


def no_auth_response():
    userinfo = {
    }

    return json.dumps(userinfo)


class TestTestController(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("before class")

    def createTestModelData(self):
        return {'name': 'test123123124'}

    def createTestHeaders(self, data):
        headers = [('Content-Type', 'application/json'),
                   ('Authorization',
                    'Bearer authorizationmockedvaluedoesntmatter')]
        if data is not None:
            json_data = json.dumps(data)
            json_data_length = len(json_data)
            headers.append(('Content-Length', str(json_data_length)))
        return headers

    @patch('pymongo.mongo_client.MongoClient', new=mongomock.MongoClient)
    def setupDatabaseRecords(self):
        with patch('mongomock.write_concern.WriteConcern.__init__',
                   return_value=None):
            data = Test(name='test_record')
            data.tenantId = "23432523452345"
            data.orgId = "987656789765670"
            data.createdBy = "1009009009988"
            data.modifiedBy = "1009009009988"
            data.createDate = str(int(time.time()))
            data.modifiedDate = str(int(time.time()))
            data.save()
            return data

    @patch('pymongo.mongo_client.MongoClient', new=mongomock.MongoClient)
    def setUp(self):
        self.data = self.setupDatabaseRecords()
        self.model_data = self.createTestModelData()
        self.headers = self.createTestHeaders(self.model_data)
        self.auth = auth_response()
        self.test_client = app.test_client()

    def tearDown(self):
        with patch('mongomock.write_concern.WriteConcern.__init__',
                   return_value=None):
            self.data.remove()

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    @patch('qube.src.api.decorators.validate_with_qubeship_auth',
           return_value=(auth_response(), 200))
    def test_post_test(self, *args, **kwargs):
        ist = io.BytesIO(json.dumps(self.model_data).encode('utf-8'))
        rv = self.test_client.post(HELLO,
                                   input_stream=ist, headers=self.headers)
        result = json.loads(rv.data.decode('utf-8'))

        self.assertTrue(rv._status_code == 201)
        Test.query.get(result['id']).remove()

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    @patch('qube.src.api.decorators.validate_with_qubeship_auth',
           return_value=(auth_response(), 200))
    def test_put_test_item(self, *args, **kwargs):
        entity_id = str(self.data.mongo_id)
        self.model_data['description'] = 'updated model desc'
        ist = io.BytesIO(json.dumps(self.model_data).encode('utf-8'))
        rv = self.test_client.put(
            HELLO_WITH_ID.format(entity_id),
            input_stream=ist, headers=self.headers)

        self.assertTrue(rv._status_code == 204)
        updated_record = Test.query.get(entity_id)
        self.assertEquals(self.model_data['description'],
                          updated_record.description)

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    @patch('qube.src.api.decorators.validate_with_qubeship_auth',
           return_value=(auth_response(), 200))
    def test_put_test_item_non_found(self, *args, **kwargs):

        ist = io.BytesIO(json.dumps(self.model_data).encode('utf-8'))
        rv = self.test_client.put(HELLO_WITH_ID.format(1234),
                                  input_stream=ist,
                                  headers=self.headers)
        self.assertTrue(rv._status_code == 404)

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    @patch('qube.src.api.decorators.validate_with_qubeship_auth',
           return_value=(auth_response(), 200))
    def test_get_test(self, *args, **kwargs):
        id_to_get = str(self.data.mongo_id)
        rv = self.test_client.get(HELLO, headers=self.headers)
        result_collection = json.loads(rv.data.decode('utf-8'))
        self.assertTrue(rv._status_code == 200,
                        "got status code " + str(rv.status_code))
        self.assertTrue(len(result_collection) == 1)
        self.assertTrue(result_collection[0].get('id') == id_to_get)
        get_record_dic = self.data.wrap()
        clean_nonserializable_attributes(get_record_dic)
        for key in get_record_dic:
            self.assertEqual(get_record_dic[key], result_collection[0].
                             get(key), "assertion failed for key {} ".
                             format(key))

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    @patch('qube.src.api.decorators.validate_with_qubeship_auth',
           return_value=(auth_response(), 200))
    def test_get_test_item(self, *args, **kwargs):
        id_to_get = str(self.data.mongo_id)
        rv = self.test_client.get(HELLO_WITH_ID.format(id_to_get),
                                  headers=self.headers)
        result = json.loads(rv.data.decode('utf-8'))
        self.assertTrue(rv._status_code == 200)
        self.assertTrue(id_to_get == result['id'])
        get_record_dic = self.data.wrap()
        clean_nonserializable_attributes(get_record_dic)
        for key in get_record_dic:
            self.assertEqual(get_record_dic[key], result.get(key),
                             "assertion failed for key {} ".format(key))

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    @patch('qube.src.api.decorators.validate_with_qubeship_auth',
           return_value=(auth_response(), 200))
    def test_get_test_item_not_found(self, *args, **kwargs):
        rv = self.test_client.get(HELLO_WITH_ID.format(12345),
                                  headers=self.headers)
        self.assertTrue(rv._status_code == 404)

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    @patch('qube.src.api.decorators.validate_with_qubeship_auth',
           return_value=(system_user_auth_response(), 200))
    def test_delete_test_item(self, *args, **kwargs):
        id_to_delete = str(self.data.mongo_id)
        rv = self.test_client.delete(HELLO_WITH_ID.format(id_to_delete),
                                     headers=self.headers)
        self.assertTrue(rv._status_code == 204)
        deleted_record = Test.query.get(id_to_delete)
        self.assertIsNone(deleted_record)

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    @patch('qube.src.api.decorators.validate_with_qubeship_auth',
           return_value=(system_user_auth_response(), 200))
    def test_delete_test_item_notfound(self, *args, **kwargs):

        rv = self.test_client.delete(HELLO_WITH_ID.format(123456),
                                     headers=self.headers)
        self.assertTrue(rv._status_code == 404)

    @patch('mongomock.write_concern.WriteConcern.__init__',
           return_value=None)
    @patch('qube.src.api.decorators.validate_with_qubeship_auth',
           return_value=(no_auth_response(), 401))
    def test_get_test_not_authorized(self, *args, **kwargs):
        rv = self.test_client.get(HELLO, headers=self.headers)
        self.assertTrue(rv._status_code == 401)

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    @patch('qube.src.api.decorators.validate_with_qubeship_auth',
           return_value=(invalid_auth_response(), 200))
    def test_get_test_master_token(self, *args, **kwargs):
        rv = self.test_client.get(HELLO, headers=self.headers)
        self.assertTrue(rv._status_code == 403)

    @patch('mongomock.write_concern.WriteConcern.__init__', return_value=None)
    @patch('qube.src.api.decorators.validate_with_qubeship_auth',
           return_value=(no_auth_response(), 401))
    def test_get_test_no_authorization(self, *args, **kwargs):
        rv = self.test_client.get(HELLO,
                                  headers=[('Content-Type',
                                            'application/json')])
        self.assertTrue(rv._status_code == 401)

    @classmethod
    def tearDownClass(cls):
        print("After class")


if __name__ == '__main__':
    unittest.main()
