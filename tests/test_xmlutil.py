import os
import sys
_mydir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(_mydir + '/..')

from xmlutil import XMLStruct

xml1 = '<top><child name="child1" id="0xe2">hello</child></top>'

def test_parse():
    top = XMLStruct(xml1)
    assert top.child["name"] == "child1"
    assert top.child.get("name") == "child1"
    assert top.child.get("name", "blah") == "child1"
    assert top.child.get("nome", "blah") == "blah"
    # Access attributes as "members"
    assert top.child.name == "child1"

def test_str():
    top = XMLStruct(xml1)
    assert str(top.child) == "XMLStruct('child', name='child1', id='0xe2')"

def test_text():
    top = XMLStruct(xml1)
    assert top.child.text == "hello"

def test_attr_as_int():
    top = XMLStruct(xml1)
    assert top.child["id"] == 0xe2
    assert top.child.id == 0xe2

xml1e = '<top><num></num><child name="child1"></child></top>'

def test_empty_tag():
    top = XMLStruct(xml1e)
    assert top.num == ""
    assert top.child == ""

xml2 = '''
<top>
<messages>
 <message name="msg1">
  <field name="field1">
   <start>0</start>
   <size>0x8</size>
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
   <size>16</size>
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

def test_find():
    top = XMLStruct(xml2)
    msg2 = top.messages("message", name="msg2")
    assert msg2['name'] == 'msg2'

def test_first_item():
    top = XMLStruct(xml2)
    assert top.messages.message['name'] == 'msg1'

def test_autoint():
    top = XMLStruct(xml2)
    f = top.messages.message.field
    assert f.start == 0
    assert f.size == 8
    msg2 = top.messages("message", name="msg2")
    # try sorting by start bit
    s = [f.description for f in sorted(msg2, key=lambda f: f.start)]
    assert s == ['Feld #1', 'Feld #3', 'Feld #2']

###

def test_file():
    top = XMLStruct(_mydir + '/plant_catalog.xml')
    assert len(top) == 36

def test_dict_by_attr():
    top = XMLStruct(xml2)
    msg = top.messages.message
    name2field = msg.as_dict('name')
    assert len(name2field) == 3
    assert name2field['field3'].description == 'Field #3'

def test_dict_by_tag():
    top = XMLStruct(_mydir + '/plant_catalog.xml')
    name2plant = top.as_dict('COMMON')
    assert len(name2plant) == 36
    assert name2plant["Dutchman's-Breeches"].BOTANICAL == 'Dicentra cucullaria'

def test_dumps():
    top = XMLStruct(_mydir + '/plant_catalog.xml')
    assert top.PLANT.dumps() == """<?xml version="1.0" encoding="UTF-8"?>
<PLANT>
  <COMMON>Bloodroot</COMMON>
  <BOTANICAL>Sanguinaria canadensis</BOTANICAL>
  <ZONE>4</ZONE>
  <LIGHT>Mostly Shady</LIGHT>
  <PRICE>$2.44</PRICE>
  <AVAILABILITY>31599</AVAILABILITY>
</PLANT>
"""
    assert top.dumps()
    xml1 = XMLStruct('<top><child name="child1">hello</child></top>')
    assert xml1.dumps() == """<?xml version="1.0" encoding="UTF-8"?>
<top>
  <child name="child1">
  </child>
</top>
"""

def test_equality():
    top1 = XMLStruct(_mydir + '/plant_catalog.xml')
    top2 = XMLStruct(_mydir + '/plant_catalog.xml')
    assert top1 == top2
    assert not (top1 != top2)
    xml1 = XMLStruct('<top><child name="child1"><val>100 </val></child></top>')
    xml2 = XMLStruct('<top><child name="child1"><val>0x64</val></child></top>')
    xml3 = XMLStruct('<top><child name="child1"><val>0x65</val></child></top>')
    xml4 = XMLStruct('<top><child name="child2"><val>0x64</val></child></top>')
    xml5 = XMLStruct('<top></top>')
    xml6 = XMLStruct('''<top><child name="child1"><val>0x64</val></child>
                     <child name="child1"><val>0x64</val></child></top>''')
    assert xml1 == xml2 and xml2 == xml1
    assert xml3 != xml2 and xml2 != xml3
    assert xml4 != xml2 and xml2 != xml4
    assert xml5 != xml2 and xml2 != xml5
    assert xml6 != xml2 and xml2 != xml6

def test_set_attr():
    xml1 = XMLStruct('<top><child name="child1">hello</child></top>')
    xml2 = XMLStruct('<top><child name="child2">hello</child></top>')
    assert xml1 != xml2
    xml2.child["name"] = "child1"
    assert xml1 == xml2
    xml2.child["foo"] = "bar"
    assert '<child foo="bar" name="child1">' in xml2.dumps()

def test_set_content():
    xml1 = XMLStruct('<top><child>hello</child><num>10</num></top>')
    xml2 = XMLStruct('<top><child>there</child><num>12</num></top>')
    assert xml1 != xml2
    xml2.child = "hello"
    xml2.num = 10
    assert xml1 == xml2
    assert '<child>hello</child>' in xml2.dumps()
    assert '<num>10</num>' in xml2.dumps()

#def test_create():
#    xml = XMLStruct('top', foo="bar")
#    xml.append('elems', num=5)
#    assert xml('elems', num=5)
#    xml.elems.append("elem", "Element 1", name="elem1")
#    xml.elems.append("elem", "Element 2", name="elem2")
#    xml.elems.append("elem", "Element 3", name="elem3")
#    print xml.dumps()
#    assert 0
#
