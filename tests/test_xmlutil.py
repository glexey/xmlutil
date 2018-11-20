import os
import sys
_mydir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(_mydir + '/..')

from xmlutil import XMLStruct

xml1 = '<top><child name="child1">hello</child></top>';

def test_parse():
    top = XMLStruct(xml1)
    assert top.child["name"] == "child1"
    assert top.child.get("name") == "child1"
    assert top.child.get("name", "blah") == "child1"
    assert top.child.get("nome", "blah") == "blah"

def test_str():
    top = XMLStruct(xml1)
    assert str(top.child) == "hello"

def test_text():
    top = XMLStruct(xml1)
    assert top.child == "hello"
    assert top.child != "hullo"
