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

import logging
import cmdb.process_management.service
import cmdb.exportd.exporter_base
from cmdb.data_storage import DatabaseManagerMongo, MongoConnector
from cmdb.utils.system_reader import SystemConfigReader

LOGGER = logging.getLogger(__name__)


class ExportdService(cmdb.process_management.service.AbstractCmdbService):

    def __init__(self):
        super(ExportdService, self).__init__()
        self._name = "exportd"
        self._eventtypes = ["cmdb.core.object.#",
                            "cmdb.core.objects.#",
                            "cmdb.core.objecttype.#",
                            "cmdb.core.objecttypes.#",
                            "cmdb.exportd.#"]

    def _run(self):
        # ToDo: for testing only
        # time.sleep(5)
        # self.__schedule_job()
        pass

    def _handle_event(self, event):
        event_type = event.get_type()
        LOGGER.debug("event received: {}".format(event_type))
        # ToDo: schedule jobs
        if event_type == "cmdb.exportd.run_manual":
            self.__schedule_job(event)

    def __schedule_job(self, event):
        from cmdb.exportd.exportd_job.exportd_job_manager import exportd_job_manager
        # ToDo: schedule job only and handle execution in _run() (own thread)
        scr = SystemConfigReader()
        database_options = scr.get_all_values_from_section('Database')
        obj = exportd_job_manager.get_job(event.get_param("id"))
        job = cmdb.exportd.exporter_base.ExportJob(obj, database_manager=DatabaseManagerMongo(
            connector=MongoConnector(
                **database_options
            )
        ))
        job.execute()
