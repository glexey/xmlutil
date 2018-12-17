import os
import re
import sys
_mydir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(_mydir + '/..')

from builtins import int as long

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
    """
    For elements with no children, str() should return element text.
    For element with children, str() is same as repr()
    """
    top = XMLStruct(xml1)
    assert str(top) == repr(top)
    assert str(top) == "XMLStruct('top')"
    assert str(top.child) == "hello"
    assert repr(top.child) == repr("hello")

def test_text():
    top = XMLStruct(xml1)
    assert top.child.text == "hello"

def test_attr_as_int():
    top = XMLStruct(xml1)
    assert top.child["id"] == 0xe2
    assert top.child.id == 0xe2
    assert repr(top.child.id) == repr(0xe2)

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
    assert repr(f.size) == repr(8)
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

def test_dumps1():
    top = XMLStruct(_mydir + '/plant_catalog.xml')
    assert top.PLANT.dumps() == """<?xml version="1.0" encoding="UTF-8"?>
<PLANT>
  <COMMON>Bloodroot</COMMON>
  <BOTANICAL>Sanguinaria canadensis</BOTANICAL>
  <description>
                    Foo
                    Bar
  </description>
  <ZONE>4</ZONE>
  <LIGHT>Mostly Shady</LIGHT>
  <PRICE>$2.44</PRICE>
  <AVAILABILITY>031599</AVAILABILITY>
</PLANT>
"""
    assert top.dumps()

def test_dumps2():
    xml1 = XMLStruct('<top><child name="child1">hello</child></top>')
    assert xml1.dumps() == """<?xml version="1.0" encoding="UTF-8"?>
<top>
  <child name="child1">hello</child>
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

    assert not (xml1 == None)
    assert not (None == xml1)
    assert xml1 != None
    assert None != xml1

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

def test_longint():
    xml1 = XMLStruct('<top><child>hello</child><num>0xFFFFFFFF</num></top>')
    assert xml1.num == 0xFFFFFFFF

def test_set_other_member():
    xml1 = XMLStruct('<top><child><another>hello</another></child></top>')
    xml1.dataclass = "345"
    assert xml1.dataclass == "345"
    xml1.child.dataclass = "123"
    assert xml1.child.dataclass == "123"
    xml1.child.another.dataclass = "xxx"
    assert xml1.child.another.dataclass == "xxx"
    for a in xml1:
        assert a.dataclass == "123" # non-XML members don't get converted

def test_same_obj():
    top = XMLStruct('<top><a><a1>a1text</a1></a><a><a1>a1text2</a1></a><b><b1>b1text</b1></b><b><b1>b1text2</b1></b></top>')
    aa = list(top)
    assert id(aa[0]) == id(top.a)
    assert id(aa[0]) == id(top("a"))
    assert id(aa[2]) == id(top.b)
    assert id(aa[2]) == id(top("b"))
    bb = list(top.a)
    assert id(bb[0]) == id(top.a.a1)

def test_numerics():
    top = XMLStruct('<top><a>10</a><b>5</b><c>0</c></top>')
    a = top.a
    b = top.b

    assert a
    assert not top.c
    
    assert a > b
    assert a >= b
    assert b < a
    assert b <= a
    assert a + b == 15
    assert a + 2 == 12
    assert 2 + a == 12
    assert a - b == 5
    assert a - 1 == 9
    assert 1 - a == -9
    assert a * b == 50
    assert a * 3 == 30
    assert 3 * a == 30
    assert a / b == 10 / 5, 10 / 5
    assert a / 4 == 10 / 4, 10 / 4
    assert 4 / a == 4 / 10, 4 / 10
    assert a / 4. == 2.5, 10 / 4.
    assert 4. / a == 0.4, 4. / 10
    assert a // b == 2
    assert a // 3 == 3
    assert 23 // a == 2
    assert a ** b == 100000
    assert a ** 3 == 1000, a ** 3
    assert 2 ** a == 1024
    assert abs(a) == 10
    assert -a == -10
    assert a % b == 0
    assert a % 3 == 1
    assert 23 % a == 3
    assert a >> b == 0
    assert a >> 1 == 5
    assert 33333 >> a == 32
    assert a << b == 320
    assert a << 1 == 20
    assert 1 << a == 1024
    assert ~a == -11

    assert a.__float__() / 3 == 10. / 3

    assert float(a) / 3 == float(10) / 3
    assert int(a) == int(10)
    assert long(a) == long(10)
    assert oct(a) == oct(10)
    assert hex(a) == hex(10)

    assert range(a) == range(10)

    assert a.bit_length() == 4

def test_str_ops():
    top = XMLStruct('<top><c>cqc</c><d>dqd</d><e></e><f>   a s d   </f></top>')

    c = top.c
    d = top.d

    assert c
    assert not top.e
    
    assert c + d == "cqcdqd"
    assert c + "aaa" == "cqcaaa"
    assert "aaa" + c == "aaacqc"

    assert c.startswith("cq")
    assert d.endswith("qd")

    assert c.replace('c', 'w') == "wqw"

    assert "qd" in d

    assert d in ["assdf", "dqd"]

    assert len(d) == 3

    assert d.upper() == "DQD"
    assert d.lower() == "dqd"

    f = top.f
    assert f.rstrip() == "   a s d"
    assert d.rstrip("d") == "dq"
    assert f.lstrip() == "a s d   "
    assert d.lstrip("d") == "qd"
    assert f.strip() == "a s d"
    assert d.strip("d") == "q"
    assert f.split() == ["a", "s", "d"]
    assert f.split(" ") == ['', '', '', 'a', 's', 'd', '', '', '']

def test_buffer_interface():
    """
    Buffer interface doesn't work, as it can only be implemented in C
    So we have to convert element to `str` to be able to re.sub() on it,
    or do file.write() on it
    """
    top = XMLStruct('<top><child>hello</child></top>')
    a = re.sub('l', 'x', str(top.child))
    assert a == 'hexxo'

def test_iterfind():
    top = XMLStruct('<top><num>10</num><s>hello</s><num>20</num><s>world</s></top>')
    nums = list(top.iterfind('num'))
    assert nums == [10, 20]
    ss = list(top.iterfind('s'))
    assert ss == ['hello', 'world']

def test_hash():
    top = XMLStruct('<top><child>hello</child></top>')
    a = {top.child: 123}
    assert a['hello'] == 123

#def test_create():
#    xml = XMLStruct('top', foo="bar")
#    xml.append('elems', num=5)
#    assert xml('elems', num=5)
#    xml.elems.append("elem", "Element 1", name="elem1")
#    xml.elems.append("elem", "Element 2", name="elem2")
#    xml.elems.append("elem", "Element 3", name="elem3")
#    assert 0
#
