#!/usr/bin/python
"""
Add docstring here
"""

from logging.config import fileConfig
import os

from flask_restful_swagger_2 import Api, swagger
from pkg_resources import resource_filename
from qube.src.api import app  # pylint: disable=import-self
from qube.src.api.flask_swagger_ui import get_swaggerui_blueprint
from qube.src.api.testcontroller import TestController
from qube.src.api.testcontroller import TestItemController
from qube.src.api.versioncontroller import TestItemVersionController
from qube.src.commons.log import Log as LOG

logging_config = resource_filename(
    'qube.src.resources', 'logging_config.ini')
fileConfig(logging_config)


# noinspection PyUnusedLocal,PyUnusedLocal,PyUnusedLocal
# pylint: disable=unused-argument
def auth(*args):
    """
    Space for your fancy authentication. Return True if access is granted,
    otherwise False
    """
    return True


swagger.auth = auth

API_URL = '/specs'  # Our API url (can of course be a local resource)

# api = Api(app, api_version='0.1', api_spec_url=API_URL)
api = Api(app, api_version='0.1', api_spec_url=API_URL)

DEFAULT_HOST = os.getenv('DEFAULT_LISTENER_HOST', 'localhost')
DEFAULT_PORT = int(os.environ.get('DEFAULT_LISTENER_PORT', '5000'))
DEBUG = os.environ.get('DEBUG', 'False') in (
    "yes", "y", "true", "True", "t", "1"
)

SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI (without trailing '/')

# Call factory function to create our blueprint
swaggerui_blueprint = get_swaggerui_blueprint(
    # Swagger UI static files will be mapped to '{SWAGGER_URL}/assets/'
    SWAGGER_URL,
    API_URL + ".json",
    # config={ # Swagger UI config overrides
    # 'supportedSubmitMethods': ['get']
    # }
)
"""
docs = []

docs.append(api.get_swagger_doc())
# Register blueprint at URL
# (URL must match the one given to factory function above)
#app.register_blueprint(get_swagger_blueprint
(docs, API_URL+'.json', title='Example', api_version='0.1'))
"""
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
api.add_resource(TestItemVersionController, '/v1/test/version')
api.add_resource(TestController, '/v1/test')
api.add_resource(TestItemController, '/v1/test/<string:entity_id>')


def main():
    """ main
    """
    app.secret_key = os.urandom(24)
    LOG.info("starting app...")
    app.run(debug=DEBUG,
            host=DEFAULT_HOST,
            port=DEFAULT_PORT)


if __name__ == '__main__':
    main()
