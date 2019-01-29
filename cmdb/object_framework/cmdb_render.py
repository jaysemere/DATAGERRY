"""OBJECT RENDER
"""
from cmdb.utils.error import CMDBError
from cmdb.object_framework import CmdbObject, CmdbType
from cmdb.object_framework.cmdb_object_field_type import CmdbFieldType
from cmdb.object_framework.cmdb_log import CmdbLog
from cmdb.utils.logger import get_logger

LOGGER = get_logger()


class CmdbRender:

    VIEW_MODE = 0
    EDIT_MODE = 1
    DEFAULT_MODE = VIEW_MODE

    POSSIBLE_INPUT_FORM_TYPES = ['text', 'password', 'email', 'tel']
    POSSIBLE_RENDER_MODES = [VIEW_MODE, EDIT_MODE]

    def __init__(self, object_instance: CmdbObject, type_instance: CmdbType, mode: int=DEFAULT_MODE):
        self.object_instance = object_instance
        self.type_instance = type_instance
        if mode not in CmdbRender.POSSIBLE_RENDER_MODES:
            raise RenderModeError()
        self.mode = mode

    def get_mode(self) -> int:
        return self.mode

    def has_external(self) -> bool:
        if len(self.type_instance.render_meta['external']) != 0:
            return True
        return False

    def all_externals_empty(self) -> bool:
        empty = True
        for external in self.type_instance.render_meta['external']:
            for field in external['fields']:
                field = self.object_instance.get_value(field)
                if field is not None:
                    empty = False
                    return empty
        return empty

    @property
    def object_instance(self) -> CmdbObject:
        return self._object_instance

    @object_instance.setter
    def object_instance(self, object_instance: CmdbObject):
        if not isinstance(object_instance, CmdbObject):
            raise ObjectInstanceError()
        self._object_instance = object_instance

    @property
    def type_instance(self) -> CmdbType:
        return self._type_instance

    @type_instance.setter
    def type_instance(self, type_instance: CmdbType):
        if not isinstance(type_instance, CmdbType):
            raise ObjectInstanceError()
        self._type_instance = type_instance

    def get_logs(self) -> (list, None):
        LOGGER.debug("LOG Size: {}".format(len(self.object_instance.get_logs())))
        log_list = []
        for log in self.object_instance.get_logs():
            try:
                tmp_log = CmdbLog(**log)
                log_list.append(tmp_log)
            except CMDBError:
                continue
        return log_list

    def get_field(self, name):
        if self.mode == self.VIEW_MODE:
            try:
                object_value = self.object_instance.get_value(name)
                # LOGGER.debug("OBJECTVALUE for Field {}: - {}".format(name, object_value))
                if object_value is None or object_value == '':
                    return None
            except CMDBError:
                return None
        try:
            field = self.type_instance.get_field(name)
            object_value = self.object_instance.get_value(name)
            if object_value is not None or object_value != '':
                enc_value = CmdbRender.field_encoder(field, object_value)
                field.set_value(enc_value)
        except CMDBError:
            return None
        return field

    @staticmethod
    def field_encoder(field: CmdbFieldType, value):
        if field.get_type() == 'date':
            LOGGER.debug("Current field TYPE: {} | VALUE: {}".format(field.get_type(), value))
            str_date_value = value.strftime("%Y-%m-%dT%H:%M")
            LOGGER.debug("Current field VALUE: {} | NEW VALUE: {}".format(value, str_date_value))
            return str_date_value
        else:
            return value
        return value


class RenderModeError(CMDBError):
    def __init__(self):
        super(CMDBError, self)
        self.message = "No possible render mode"


class ObjectInstanceError(CMDBError):
    def __init__(self):
        super(CMDBError, self)
        self.message = "Wrong instance"


class InvalidHtmlInputType(CMDBError):
    def __init__(self, html_type):
        super(CMDBError, self)
        self.message = "Input type {} is not supported".format(html_type)