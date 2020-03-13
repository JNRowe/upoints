#
"""utils - Utilities for test support."""
# Copyright © 2013-2017  James Rowe <jnrowe@gmail.com>
#
# This file is part of upoints.
#
# upoints is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# upoints is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# upoints.  If not, see <http://www.gnu.org/licenses/>.

from doctest import _ellipsis_match as ellipsis_match

from lxml import etree


def xml_compare(elem1, elem2, ellipsis=False):
    """Compare XML elements

    Args:
        ellipsis (bool): Support ellipsis for 'any' match

    Raises:
        ValueError: On mismatch in ellipsised text
    """
    assert elem1.tag == elem2.tag
    for key, value in elem1.attrib.items():
        assert elem2.attrib.get(key) == value
    for key in elem2.attrib.keys():
        assert key in elem1.attrib
    text1 = elem1.text.strip() if elem1.text else ''
    text2 = elem2.text.strip() if elem2.text else ''
    tail1 = elem1.tail.strip() if elem1.tail else ''
    tail2 = elem2.tail.strip() if elem2.tail else ''
    if ellipsis:
        if not ellipsis_match(text1, text2):
            raise ValueError(f'text mismatch: {elem1.text!r} != {elem2.text!r}')
        if not ellipsis_match(tail1, tail2):
            raise ValueError(f'tail mismatch: {elem1.tail!r} != {elem2.tail!r}')
    else:
        assert text1 == text2
        assert tail1 == tail2
    children1 = elem1.getchildren()
    children2 = elem2.getchildren()
    assert len(children1) == len(children2)
    for child1, child2 in zip(children1, children2):
        xml_compare(child1, child2, ellipsis)


def xml_str_compare(string1, string2, ellipsis=False):
    """Compare XML string representations

    Args:
        ellipsis (bool): Support ellipsis for 'any' match
    """
    doc1 = etree.fromstring(string1)
    doc2 = etree.fromstring(string2)
    xml_compare(doc1, doc2, ellipsis)
