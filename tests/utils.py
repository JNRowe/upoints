#
# coding=utf-8
"""utils - Utilities for test support"""
# Copyright © 2007-2014  James Rowe <jnrowe@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from doctest import _ellipsis_match as ellipsis_match

from expecter import expect
from lxml import etree


def xml_compare(elem1, elem2, ellipsis=False):
    expect(elem1.tag) == elem2.tag
    for key, value in elem1.attrib.items():
        expect(elem2.attrib.get(key)) == value
    for key in elem2.attrib.keys():
        expect(elem1.attrib).contains(key)
    text1 = elem1.text.strip() if elem1.text else ''
    text2 = elem2.text.strip() if elem2.text else ''
    tail1 = elem1.tail.strip() if elem1.tail else ''
    tail2 = elem2.tail.strip() if elem2.tail else ''
    if ellipsis:
        if not ellipsis_match(text1, text2):
            raise ValueError('text mismatch: %r != %r' % (elem1.text,
                                                          elem2.text))
        if not ellipsis_match(tail1, tail2):
            raise ValueError('tail mismatch: %r != %r' % (elem1.text,
                                                          elem2.text))
    else:
        expect(text1) == text2
        expect(tail1) == tail2
    children1 = elem1.getchildren()
    children2 = elem2.getchildren()
    expect(len(children1)) == len(children2)
    for child1, child2 in zip(children1, children2):
        xml_compare(child1, child2, ellipsis)


def xml_str_compare(string1, string2, ellipsis=False):
    doc1 = etree.fromstring(string1)
    doc2 = etree.fromstring(string2)
    xml_compare(doc1, doc2, ellipsis)
