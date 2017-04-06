#!/usr/bin/python
"""
Add docstring here
"""
import json
import os
import unittest

from mock import patch
import mongomock

from pkg_resources import resource_filename
from qube.src.commons.qube_config import QubeConfig

HELLO_VERSION = "/v1/test/version"
with patch('pymongo.mongo_client.MongoClient', new=mongomock.MongoClient):
    os.environ['TEST_MONGOALCHEMY_CONNECTION_STRING'] = ''
    os.environ['TEST_MONGOALCHEMY_SERVER'] = ''
    os.environ['TEST_MONGOALCHEMY_PORT'] = ''
    os.environ['TEST_MONGOALCHEMY_DATABASE'] = ''
    from qube.src.api.app import app


class TestTestVersionController(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("setup")

    def setUp(self):
        self.test_client = app.test_client()

    def tearDown(self):
        print("teardown")

    def test_test_default_version(self, *args, **kwargs):
        QubeConfig.get_config().QUBE_VERSION_FILE = resource_filename(
            'qube.src.resources', 'qube_sample_version_dontexist.txt')
        QubeConfig.get_config().version_str = None
        rv = self.test_client.get(HELLO_VERSION,
                                  headers=[('Content-Type',
                                            'application/json')])
        result = json.loads(rv.data.decode('utf-8'))
        self.assertTrue(rv._status_code == 200)
        self.assertEquals(result['version'],
                          QubeConfig.get_config().default_ver)

    def test_test_git_version(self, *args, **kwargs):
        QubeConfig.get_config().QUBE_VERSION_FILE = resource_filename(
            'qube.src.resources', 'qube_sample_version.txt')
        QubeConfig.get_config().version_str = None
        with open(QubeConfig.get_config().QUBE_VERSION_FILE, 'r') as f:
            expected_version_str_file = f.read()

        expected_version_string = "{} ({})". \
            format(QubeConfig.get_config().default_ver,
                   expected_version_str_file.strip())

        rv = self.test_client.get(HELLO_VERSION,
                                  headers=[('Content-Type',
                                            'application/json')])
        result = json.loads(rv.data.decode('utf-8'))
        self.assertTrue(rv._status_code == 200)
        self.assertEquals(result['version'], expected_version_string)

    @classmethod
    def tearDownClass(cls):
        print("After class")


if __name__ == '__main__':
    unittest.main()
