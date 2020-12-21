# DATAGERRY - OpenSource Enterprise CMDB
# Copyright (C) 2019 NETHINKS GmbH
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
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


import json
import logging

from flask import request, abort
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from werkzeug.wrappers import Request

from cmdb.framework.managers.type_manager import TypeManager
from cmdb.user_management import UserModel
from cmdb.security.acl.errors import AccessDeniedError
from cmdb.security.acl.permission import AccessControlPermission
from cmdb.framework.models.type import TypeModel

LOGGER = logging.getLogger(__name__)


def get_file_in_request(file_name: str, request_files) -> FileStorage:
    if file_name not in request_files:
        LOGGER.error(f'File with name: {file_name} was not provided')
        return abort(400)
    return request.files.get(file_name)


def get_element_from_data_request(element, _request: Request) -> (dict, None):
    try:
        return json.loads(_request.form.to_dict()[element])
    except (KeyError, Exception):
        return None


def generate_parsed_output(request_file, file_format, parser_config):
    from cmdb.importer import load_parser_class
    # Load parser class
    parser_class = load_parser_class('object', file_format)

    # save file
    filename = secure_filename(request_file.filename)
    working_file = f'/tmp/{filename}'
    request_file.save(working_file)

    # parse content
    parser = parser_class(parser_config)
    output = parser.parse(working_file)
    return output


def verify_import_access(user: UserModel, _type: TypeModel, _manager: TypeManager):
    """Validate if a user has access to objects of this type."""

    location = 'acl.groups.includes.' + str(user.group_id)
    query = {'$and': [{'$or': [
        {'$or': [
            {'acl': {'$exists': False}}, {'acl.activated': False}]
        },
        {'$and': [
            {'acl.activated': True},
            {'$and': [
                {location: {'$exists': True}},
                {location: {'$all': [
                    AccessControlPermission.READ.value,
                    AccessControlPermission.CREATE.value,
                    AccessControlPermission.UPDATE.value]
                    }
                }
            ]
            }
        ]
        }]
    }, {'public_id': _type.public_id}]}
    types_ = _manager.iterate(filter=query, limit=1, skip=0, sort='public_id', order=1)
    if len([TypeModel.to_json(_) for _ in types_.results]) == 0:
        raise AccessDeniedError(f'The objects of the type `{_type.name}` are protected by ACL permission!')

