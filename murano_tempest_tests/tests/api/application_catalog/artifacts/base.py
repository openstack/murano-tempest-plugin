# Copyright (c) 2016 Mirantis, Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from tempest.common import credentials_factory as common_creds
from tempest import config
from tempest.lib import base

from murano_tempest_tests import clients
from murano_tempest_tests import utils

CONF = config.CONF


class BaseArtifactsTest(base.BaseTestCase):
    """Base test class for Murano Glare tests."""

    @classmethod
    def setUpClass(cls):
        super(BaseArtifactsTest, cls).setUpClass()
        cls.resource_setup()

    @classmethod
    def tearDownClass(cls):
        cls.resource_cleanup()
        super(BaseArtifactsTest, cls).tearDownClass()

    @classmethod
    def get_client_with_isolated_creds(cls, type_of_creds="admin"):

        creds = cls.get_configured_isolated_creds(type_of_creds=type_of_creds)

        os = clients.Manager(credentials=creds)
        client = os.artifacts_client

        return client

    @classmethod
    def get_configured_isolated_creds(cls, type_of_creds='admin'):
        identity_version = CONF.identity.auth_version
        if identity_version == 'v3':
            cls.admin_role = CONF.identity.admin_role
        else:
            cls.admin_role = 'admin'
        cls.credentials = common_creds.get_credentials_provider(
            name=cls.__name__,
            force_tenant_isolation=CONF.auth.use_dynamic_credentials,
            identity_version=CONF.identity.auth_version)
        if type_of_creds == 'primary':
            creds = cls.credentials.get_primary_creds()
        elif type_of_creds == 'admin':
            creds = cls.credentials.get_admin_creds()
        elif type_of_creds == 'alt':
            creds = cls.credentials.get_alt_creds()
        else:
            creds = cls.credentials.get_credentials(type_of_creds)
        cls.credentials.type_of_creds = type_of_creds

        return creds.credentials

    @classmethod
    def verify_nonempty(cls, *args):
        if not all(args):
            msg = "Missing API credentials in configuration."
            raise cls.skipException(msg)

    @classmethod
    def resource_setup(cls):
        if not CONF.service_available.murano:
            skip_msg = "Murano is disabled"
            raise cls.skipException(skip_msg)
        if not hasattr(cls, "os"):
            creds = cls.get_configured_isolated_creds(type_of_creds='primary')
            cls.os = clients.Manager(credentials=creds)
        cls.artifacts_client = cls.os.artifacts_client
        cls.application_catalog_client = cls.os.application_catalog_client

    @classmethod
    def resource_cleanup(cls):
        cls.clear_isolated_creds()

    @classmethod
    def clear_isolated_creds(cls):
        if hasattr(cls, "dynamic_cred"):
            cls.credentials.clear_creds()

    @classmethod
    def upload_package(cls, application_name, version=None, require=None):
        abs_archive_path, dir_with_archive, archive_name = \
            utils.prepare_package(application_name, version=version,
                                  add_class_name=True, require=require)
        package = cls.artifacts_client.upload_package(
            application_name, archive_name, dir_with_archive,
            {"categories": [], "tags": [], 'is_public': False})
        return package, abs_archive_path

    @staticmethod
    def create_obj_model(package):
        return {
            "name": package['display_name'],
            "?": {
                "type": package['name'],
                "id": utils.generate_uuid(),
                "classVersion": package['version']
            }
        }
