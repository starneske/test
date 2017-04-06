#!/usr/bin/python
"""
Add docstring here
"""
from flask import request
from flask_restful_swagger_2 import Resource, swagger
from mongoalchemy.exceptions import ExtraValueException

from qube.src.api.decorators import login_required
from qube.src.api.swagger_models.test import TestModel # noqa: ignore=I100
from qube.src.api.swagger_models.test import TestModelPost # noqa: ignore=I100
from qube.src.api.swagger_models.test import TestModelPostResponse # noqa: ignore=I100
from qube.src.api.swagger_models.test import TestModelPut # noqa: ignore=I100

from qube.src.api.swagger_models.parameters import (
    body_post_ex, body_put_ex, header_ex, path_ex, query_ex)
from qube.src.api.swagger_models.response_messages import (
    del_response_msgs, ErrorModel, get_response_msgs, post_response_msgs,
    put_response_msgs)
from qube.src.commons.error import TestServiceError
from qube.src.commons.log import Log as LOG
from qube.src.commons.utils import clean_nonserializable_attributes
from qube.src.services.testservice import TestService

EMPTY = ''
get_details_params = [header_ex, path_ex, query_ex]
put_params = [header_ex, path_ex, body_put_ex]
delete_params = [header_ex, path_ex]
get_params = [header_ex]
post_params = [header_ex, body_post_ex]


class TestItemController(Resource):
    @swagger.doc(
        {
            'tags': ['Test'],
            'description': 'Test get operation',
            'parameters': get_details_params,
            'responses': get_response_msgs
        }
    )
    @login_required
    def get(self, authcontext, entity_id):
        """gets an test item that omar has changed
        """
        try:
            LOG.debug("Get details by id %s ", entity_id)
            data = TestService(authcontext['context'])\
                .find_by_id(entity_id)
            clean_nonserializable_attributes(data)
        except TestServiceError as e:
            LOG.error(e)
            return ErrorModel(**{'error_code': str(e.errors.value),
                                 'error_message': e.args[0]}), e.errors
        except ValueError as e:
            LOG.error(e)
            return ErrorModel(**{'error_code': '400',
                                 'error_message': e.args[0]}), 400
        return TestModel(**data), 200

    @swagger.doc(
        {
            'tags': ['Test'],
            'description': 'Test put operation',
            'parameters': put_params,
            'responses': put_response_msgs
        }
    )
    @login_required
    def put(self, authcontext, entity_id):
        """
        updates an test item
        """
        try:
            model = TestModelPut(**request.get_json())
            context = authcontext['context']
            TestService(context).update(model, entity_id)
            return EMPTY, 204
        except TestServiceError as e:
            LOG.error(e)
            return ErrorModel(**{'error_code': str(e.errors.value),
                                 'error_message': e.args[0]}), e.errors
        except ValueError as e:
            LOG.error(e)
            return ErrorModel(**{'error_code': '400',
                                 'error_message': e.args[0]}), 400
        except Exception as ex:
            LOG.error(ex)
            return ErrorModel(**{'error_code': '500',
                                 'error_message': ex.args[0]}), 500

    @swagger.doc(
        {
            'tags': ['Test'],
            'description': 'Test delete operation',
            'parameters': delete_params,
            'responses': del_response_msgs
        }
    )
    @login_required
    def delete(self, authcontext, entity_id):
        """
        Delete test item
        """
        try:
            TestService(authcontext['context']).delete(entity_id)
            return EMPTY, 204
        except TestServiceError as e:
            LOG.error(e)
            return ErrorModel(**{'error_code': str(e.errors.value),
                                 'error_message': e.args[0]}), e.errors
        except ValueError as e:
            LOG.error(e)
            return ErrorModel(**{'error_code': '400',
                                 'error_message': e.args[0]}), 400
        except Exception as ex:
            LOG.error(ex)
            return ErrorModel(**{'error_code': '500',
                                 'error_message': ex.args[0]}), 500


class TestController(Resource):
    @swagger.doc(
        {
            'tags': ['Test'],
            'description': 'Test get operation',
            'parameters': get_params,
            'responses': get_response_msgs
        }
    )
    @login_required
    def get(self, authcontext):
        """
        gets all test items
        """
        LOG.debug("Serving  Get all request")
        list = TestService(authcontext['context']).get_all()
        # normalize the name for 'id'
        return list, 200

    @swagger.doc(
        {
            'tags': ['Test'],
            'description': 'Test create operation',
            'parameters': post_params,
            'responses': post_response_msgs
        }
    )
    @login_required
    def post(self, authcontext):
        """
        Adds a test item.
        """
        try:
            model = TestModelPost(**request.get_json())
            result = TestService(authcontext['context'])\
                .save(model)

            response = TestModelPostResponse()
            for key in response.properties:
                response[key] = result[key]

            return (response, 201,
                    {'Location': request.path + '/' + str(response['id'])})
        except ValueError as e:
            LOG.error(e)
            return ErrorModel(**{'error_code': str(e.errors.value),
                                 'error_message': e.args[0]}), 400
        except ExtraValueException as e:
            LOG.error(e)
            return ErrorModel(**{'error_code': '400',
                                 'error_message': "{} is not valid input".
                              format(e.args[0])}), 400
        except Exception as ex:
            LOG.error(ex)
            return ErrorModel(**{'error_code': '500',
                                 'error_message': ex.args[0]}), 500
