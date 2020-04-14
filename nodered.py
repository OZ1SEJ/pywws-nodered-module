# pywws - Python software for USB Wireless Weather Stations
# http://github.com/jim-easterbrook/pywws
# Copyright (C) 2018-20  pywws contributors

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

"""Upload current weather data to Node-RED server.

Node-RED is a data handler for linux-based operating systems, popular with the Raspberry Pi.

* Web site: http://www.nodered.org/
* Additional dependency: http://docs.python-requests.org/
* Example ``weather.ini`` configuration::

    [live]
    services = ['nodered', 'underground']

    [logged]
    services = ['nodered', 'underground']

"""

from __future__ import absolute_import, unicode_literals

from contextlib import contextmanager
from datetime import timedelta
import logging
import os
import sys

import requests

import pywws.service

__docformat__ = "restructuredtext en"
service_name = os.path.splitext(os.path.basename(__file__))[0]
logger = logging.getLogger(__name__)

class ToService(pywws.service.LiveDataService):
    config = {'hash': ('', True, 'hash')}
    logger = logger
    service_name = service_name
    template = "#live##temp_out \"'t': '%.1f',\"#"

    @contextmanager
    def session(self):
        with requests.Session() as session:
            yield session

    def valid_data(self, data):
        return data['temp_out'] is not None

    def upload_data(self, session, prepared_data={}):
        try:
            rsp = session.get('http://data:1880/wx',
                              params=prepared_data, timeout=60)
        except Exception as ex:
            return False, repr(ex)
        if rsp.status_code != 200:
            return False, 'http status: {:d}'.format(rsp.status_code)
        text = rsp.text.strip()
        if text:
            return True, 'server response "{:s}"'.format(text)
        return True, 'OK'

if __name__ == "__main__":
    sys.exit(pywws.service.main(ToService))
