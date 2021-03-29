# test.py
#
# Copyright 2021 Yevhen Shyshkan
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Tests for boincrpc module."""
import unittest
import xml.etree.ElementTree as ET
from cmd import DEFAULT_HOST, DEFAULT_PORT, get_password
from boincrpc import BoincRpc, et_find


class Test_et_find(unittest.TestCase):
    """Test et_find() function."""
    xml_string = ('<test_sample>'
                  '<one>1</one>'
                  '<two>2<two_and_five>2.5</two_and_five></two>'
                  '</test_sample>')
    sample = ET.fromstring(xml_string)

    def test_et_find_one(self):
        """Simplest case when the target is in the first layer of xml."""
        result = et_find(self.sample, 'one')
        self.assertEqual(result.text, '1')

    def test_et_find_two(self):
        """Case when target tag contains additional objects."""
        result = et_find(self.sample, 'two')
        self.assertEqual(result.text, '2')

    def test_et_find_two_and_two(self):
        """Case when target not in the first layer."""
        result = et_find(self.sample, 'two_and_five')
        self.assertEqual(result.text, '2.5')

    def test_et_find_none(self):
        """Case when target is missing in xml."""
        result = et_find(self.sample, 'three')
        self.assertEqual(result, None)


class Test_BoincRpc(unittest.TestCase):
    """Test BoincRpc class."""
    def setUp(self):
        self.password = get_password()
        self.boinc_rpc = BoincRpc(DEFAULT_HOST, DEFAULT_PORT, self.password)

    def test_simple_request(self):
        """ Check that response contains meaningful result."""
        exchange_versions = self.boinc_rpc.simple_request('exchange_versions')
        result = et_find(ET.fromstring(exchange_versions), 'major')
        # Check that respone contains some info
        self.assertEqual(result.tag, 'major')


if __name__ == '__main__':
    unittest.main()
