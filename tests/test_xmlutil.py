import os
import sys
_mydir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(_mydir + '/..')

from xmlutil import XMLStruct

xml1 = '<top><child name="child1">hello</child></top>'

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

xml2 = '''
<top>
<messages>
 <message name="msg1">
  <field name="field1">
   <start>0</start>
   <size>8</size>
   <description>Field #1</description>
  </field>
  <field name="field2">
   <start>8</start>
   <size>8</size>
   <description>Field #2</description>
  </field>
  <field name="field3">
   <start>16</start>
   <size>8</size>
   <description>Field #3</description>
  </field>
 </message>
 <message name="msg2">
  <field name="feld1">
   <start>0</start>
   <size>8</size>
   <description>Feld #1</description>
  </field>
  <field name="feld2">
   <start>16</start>
   <size>8</size>
   <description>Feld #2</description>
  </field>
  <field name="feld3">
   <start>8</start>
   <size>8</size>
   <description>Feld #3</description>
  </field>
 </message>
</messages>
</top>
'''

def test_list():
    top = XMLStruct(xml2)
    assert top.messages[0]['name'] == 'msg1'
    assert top.messages[1]['name'] == 'msg2'
    felds = top.messages[-1]
    assert felds[0]['name'] == 'feld1'
    assert felds[1]['name'] == 'feld2'
    assert felds[2]['name'] == 'feld3'

def test_iter():
    top = XMLStruct(xml2)
    msg_names = [m['name'] for m in top.messages]
    assert msg_names == ['msg1', 'msg2']
    descriptions = [f.description for f in top.messages[1]]
    assert descriptions == ['Feld #1', 'Feld #2', 'Feld #3']
