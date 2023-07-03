
# DATAGERRY - OpenSource Enterprise CMDB
# Copyright (C) 2023 becon GmbH
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

import pytest

def pytest_addoption(parser):
    parser.addoption(
        '--mongodb-host', action='store', default='localhost', help='Host of mongodb test instance'
    )
    parser.addoption(
        '--mongodb-port', action='store', default=27017, help='Port of mongodb test instance'
    )
    parser.addoption(
        '--mongodb-database', action='store', default='cmdb-test', help='Database of mongodb test instance'
    )


pytest_plugins = [
    'tests.fixtures.fixture_database',
    'tests.fixtures.fixture_management',
    'tests.fixtures.fixture_rest_api'
]


@pytest.fixture(scope="session", autouse=True)
def preset_database(database_manager, database_name):
    from cmdb.database.errors.database_errors import DatabaseNotExists
    from cmdb.security.key.generator import KeyGenerator
    from cmdb.security.security import SecurityManager
    from cmdb.user_management.managers.group_manager import GroupManager
    from cmdb.user_management.managers.user_manager import UserManager
    try:
        database_manager.drop_database(database_name)
    except DatabaseNotExists:
        pass
    from cmdb.user_management import __FIXED_GROUPS__
    from datetime import datetime

    kg = KeyGenerator(database_manager=database_manager)
    kg.generate_rsa_keypair()
    kg.generate_symmetric_aes_key()

    group_manager = GroupManager(database_manager=database_manager)
    user_manager = UserManager(database_manager=database_manager)
    security_manager = SecurityManager(database_manager=database_manager)

    for group in __FIXED_GROUPS__:
        group_manager.insert(group)

    admin_name = 'admin'
    admin_pass = 'admin'
    from cmdb.user_management import UserModel
    admin_user = UserModel(
        public_id=1,
        user_name=admin_name,
        active=True,
        group_id=__FIXED_GROUPS__[0].public_id,
        registration_time=datetime.now(),
        password=security_manager.generate_hmac(admin_pass),
    )
    user_manager.insert(admin_user)
