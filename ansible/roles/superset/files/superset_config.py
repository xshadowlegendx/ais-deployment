# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
# This file is included in the final Docker image and SHOULD be overridden when
# deploying the image to prod. Settings configured here are intended for use in local
# development environments. Also note that superset_config_docker.py is imported
# as a final step as a means to override "defaults" configured here
#
import logging
import os
import sys

from celery.schedules import crontab
from flask_caching.backends.filesystemcache import FileSystemCache

logger = logging.getLogger()

DATABASE_DIALECT = "postgresql"
DATABASE_DB = os.getenv("DATABASE_DB")

SQLALCHEMY_DATABASE_URI = (
    f"{DATABASE_DIALECT}://"
    f"/{DATABASE_DB}"
)

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_CELERY_DB = os.getenv("REDIS_CELERY_DB", "0")
REDIS_RESULTS_DB = os.getenv("REDIS_RESULTS_DB", "1")

RESULTS_BACKEND = FileSystemCache("/app/superset_home/sqllab")

CACHE_CONFIG = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_DEFAULT_TIMEOUT": 300,
    "CACHE_KEY_PREFIX": "superset_",
    "CACHE_REDIS_HOST": REDIS_HOST,
    "CACHE_REDIS_PORT": REDIS_PORT,
    "CACHE_REDIS_DB": REDIS_RESULTS_DB,
}
DATA_CACHE_CONFIG = CACHE_CONFIG
THUMBNAIL_CACHE_CONFIG = CACHE_CONFIG


class CeleryConfig:
    broker_url = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_CELERY_DB}"
    imports = (
        "superset.sql_lab",
        "superset.tasks.scheduler",
        "superset.tasks.thumbnails",
        "superset.tasks.cache",
    )
    result_backend = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_RESULTS_DB}"
    worker_prefetch_multiplier = 1
    task_acks_late = False
    beat_schedule = {
        "reports.scheduler": {
            "task": "reports.scheduler",
            "schedule": crontab(minute="*", hour="*"),
        },
        "reports.prune_log": {
            "task": "reports.prune_log",
            "schedule": crontab(minute=10, hour=0),
        },
    }


CELERY_CONFIG = CeleryConfig

FEATURE_FLAGS = {"ALERT_REPORTS": True, "DATASET_FOLDERS": True}
ALERT_REPORTS_NOTIFICATION_DRY_RUN = True
WEBDRIVER_BASEURL = f"http://superset_app{os.environ.get('SUPERSET_APP_ROOT', '/')}/"  # When using docker compose baseurl should be http://superset_nginx{ENV{BASEPATH}}/  # noqa: E501
# The base URL for the email report hyperlinks.
WEBDRIVER_BASEURL_USER_FRIENDLY = (
    f"http://localhost:8888/{os.environ.get('SUPERSET_APP_ROOT', '/')}/"
)
SQLLAB_CTAS_NO_LIMIT = True

log_level_text = os.getenv("SUPERSET_LOG_LEVEL", "INFO")
LOG_LEVEL = getattr(logging, log_level_text.upper(), logging.INFO)

if os.getenv("CYPRESS_CONFIG") == "true":
    # When running the service as a cypress backend, we need to import the config
    # located @ tests/integration_tests/superset_test_config.py
    base_dir = os.path.dirname(__file__)
    module_folder = os.path.abspath(
        os.path.join(base_dir, "../../tests/integration_tests/")
    )
    sys.path.insert(0, module_folder)
    from superset_test_config import *  # noqa

    sys.path.pop(0)

from flask_appbuilder.security.manager import AUTH_OAUTH

AUTH_TYPE = AUTH_OAUTH

OAUTH_PROVIDERS = [
    {   'name':'PocketID',
        'token_key':'access_token',
        'icon':'fa-address-card',
        'remote_app': {
            'client_id': os.getenv("SSO_OIDC_CLIENT_ID"),  # Client Id (Identify Superset application)
            'client_secret': os.getenv("SSO_OIDC_CLIENT_SECRET"), # Secret for this Client Id (Identify Superset application)
            'client_kwargs':{
                'scope': 'openid profile email roles'               # Scope for the Authorization
            },
            'jwks_uri': os.getenv("SSO_OIDC_JWKS_URI"), # may be required to generate token
            'api_base_url': os.getenv("SSO_OIDC_API_BASE_URL"),
            'access_token_url': os.getenv("SSO_OIDC_ACCESS_TOKEN_URL"),
            'authorize_url': os.getenv("SSO_OIDC_AUTHORIZE_URL")
        }
    }
]

# Will allow user self registration, allowing to create Flask users from Authorized User
AUTH_USER_REGISTRATION = False

# The default user self registration role
AUTH_USER_REGISTRATION_ROLE = "Public"

AUTH_ROLES_SYNC_AT_LOGIN = True

AUTH_ROLES_MAPPING = {
    'admin': ['Admin', 'sql_lab']
}

import logging
from superset.security import SupersetSecurityManager

class CustomSsoSecurityManager(SupersetSecurityManager):
    def oauth_user_info(self, provider, response=None):
        logging.debug("Oauth2 provider: {0}.".format(provider))
        if provider == 'PocketID':
            # As example, this line request a GET to base_url + '/' + userDetails with Bearer  Authentication,
    # and expects that authorization server checks the token, and response with user details
            userinfo = self.appbuilder.sm.oauth_remotes[provider].get("protocol/openid-connect/userinfo")
            me = userinfo.json()
            logging.info("user_data: {0}".format(me))
            return { 'name' : me['preferred_username'], 'email' : me['email'], 'id' : me['sub'], 'username' : me['preferred_username'], 'first_name': me['family_name'], 'last_name': me['given_name'], 'role_keys': me.get('roles', [])}

CUSTOM_SECURITY_MANAGER = CustomSsoSecurityManager

#
# Optionally import superset_config_docker.py (which will have been included on
# the PYTHONPATH) in order to allow for local settings to be overridden
#
try:
    import superset_config_docker
    from superset_config_docker import *  # noqa: F403

    logger.info(
        "Loaded your Docker configuration at [%s]", superset_config_docker.__file__
    )
except ImportError:
    logger.info("Using default Docker config...")

