# -*- coding: utf-8 -*-
#
# Please refer to AUTHORS.rst for a complete list of Copyright holders.
# Copyright (C) 2022-2023, Agoras Developers.

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""

agoras.common.utils
===================

This module contains common and low level functions to all modules in agoras.

"""


from urllib.parse import parse_qs, urlencode, urlparse


def add_url_timestamp(url, timestamp):
    parsed = urlparse(url)
    query = dict(parse_qs(str(parsed.query)))
    query['t'] = timestamp
    parsed = parsed._replace(query=urlencode(query))
    return parsed.geturl()
