[![Build Status](https://travis-ci.org/glexey/xmlutil.svg?branch=master)](https://travis-ci.org/glexey/xmlutil)

# xmlutil::XMLStruct

Convenience wrapper around python's `cElementtree` for working with XML data.

Goal: simplicity of working with XML that represent data structures. Non-goals: speed, supporting
all XML quirks.

## Install

    pip install xmlutil

## Usage

`xmlutil` module exposes `XMLStruct` class for representing XML data:

    >>> from xmlutil import XMLStruct

### Reading XML data

Initialize XMLStruct from string:

    >>> xml1 = '<top><child name="child1" id="0xe2">hello</child></top>'
    >>> top = XMLStruct(xml1)
    >>> top
    XMLStruct('top')
    >>> print top.dumps()
    <?xml version="1.0" encoding="UTF-8"?>
    <top>
      <child id="0xe2" name="child1">hello</child>
    </top>
    >>> open("hello.xml", "w").write(top.dumps())

Initialize XMLStruct from file:

    >>> top2 = XMLStruct("hello.xml")
    >>> top == top2
    True

As can be see in above example, operator `==` is overloaded to compare the contents of two XML
structures.

### Navigating the tree

We'll use the following XML for the examples below:

    msgs_xml = '''
     <top>
      <messages>
       <message name="DEBUG_BREAKPOINT">
        <field name="descriptor">
         <start>0</start>
         <size>0x8</size>
         <description>File descriptor</description>
        </field>
        <field name="lineno">
         <start>8</start>
         <size>8</size>
         <description>Line Number</description>
        </field>
        <field name="reason">
         <start>16</start>
         <size>8</size>
         <description>Breakpoint reason ID</description>
        </field>
       </message>
       <message name="MEMORY_ALLOC">
        <field name="base_address">
         <start>0</start>
         <size>32</size>
         <description>Memory allocation base address</description>
        </field>
        <field name="length">
         <start>32</start>
         <size>32</size>
         <description>Memory block length</description>
        </field>
        <field name="mode">
         <start>64</start>
         <size>8</size>
         <description>Allocation mode</description>
        </field>
       </message>
      </messages>
     </top>
    '''

After reading the data, XMLStruct points to the topmost element ("top" in this case):

    >>> top = XMLStruct(msgs_xml)
    >>> top
    XMLStruct('top')

First child element with a given tag name be accessed by XML tag name using `.` notation:

    >>> top.messages
    XMLStruct('messages')
    >>> top.messages.message
    XMLStruct('message', name='DEBUG_BREAKPOINT')

XML *attributes* can also be accessed using a `.` notation, and in case of ambiguity, through a
dict-like access:

    >>> top.messages.message.name
    'DEBUG_BREAKPOINT'
    >>> top.messages.message['name']
    'DEBUG_BREAKPOINT'

Children be accessed as a list:

    >>> list(top.messages)
    [XMLStruct('message', name='DEBUG_BREAKPOINT'),
     XMLStruct('message', name='MEMORY_ALLOC')]
    >>> top[0] == top.messages
    True
    >>> top.messages[1].name
    'MEMORY_ALLOC'
    >>> len(top.messages.message)
    3

Here's how we can print all message fields in this example:

    >>> for msg in top.messages:
            for field in msg:
                print "%s.%s"%(msg.name, field.name)
    DEBUG_BREAKPOINT.descriptor
    DEBUG_BREAKPOINT.lineno
    DEBUG_BREAKPOINT.reason
    MEMORY_ALLOC.base_address
    MEMORY_ALLOC.length
    MEMORY_ALLOC.mode

When attempting to access a non-existing element, `None` is returned w/o throwing errors:

    >>> print top.abc
    None

### Simple elements

Elements that have no children are *simple*.

Simple elements that contain text that looks like a numeric value, for most intents and purposes
behave like numbers:

    >>> field1 = top.messages.message.field
    >>> field1.start
    0
    >>> field1.size
    8
    >>> Field1.start + field1.size
    8

However, they are still XMLStruct():

    >>> type(field1.size)
    xmlutil.xmlstruct.XMLStruct

TODO: describe supported number formats, and turning off auto-number conversion behavior.

Simple elements that contain text that does not look like a number, for most intents and purposes
behave like strings containing the element's text:

    >>> desc1 = top.messages.message.field.description
    >>> desc1
    'File descriptor'
    >>> desc1.upper() + '#1'
    'FILE DESCRIPTOR #1'

The only exception is they can't be fed to methods requiring [buffer
protocol](https://docs.python.org/3/c-api/buffer.html#bufferobjects), such as re.search() or
file.write(). For such operations, explicitly convert the XMLStruct to `str`:

    >>> re.sub('descri', 'velocira', desc1)
    ...
    TypeError: expected string or buffer
    >>> re.sub('descri', 'velocira', str(desc1))
    'File velociraptor'

### Using XPath notation

Elements can be selected (iterated over) using XPath expressions [subset supported by
Elementtree](https://docs.python.org/2/library/xml.etree.elementtree.html#xpath-support):

    >>> list(top.iterfind('.//field'))
    [XMLStruct('field', name='descriptor'),
     XMLStruct('field', name='lineno'),
     XMLStruct('field', name='reason'),
     XMLStruct('field', name='base_address'),
     XMLStruct('field', name='length'),
     XMLStruct('field', name='mode')]

When there's just first element that needs to be located `()` notation can be used:

    >>> top('.//field')
    XMLStruct('field', name='descriptor')
    >>> top('.//field[@name="base_address"]')
    XMLStruct('field', name='base_address')

