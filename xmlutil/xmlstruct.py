import xml.etree.cElementTree as ET

class XMLStruct(object):

    def __init__(self, arg):
        if isinstance(arg, basestring):
            self.elem = ET.fromstring(arg)
        else:
            self.elem = arg
    
    def __getattr__(self, attr):
        elem = self.elem.find(attr)
        if elem is None:
            raise AttributeError("Attribute '%s' not found"%attr)
        result = XMLStruct(elem)
        return result

    def __getitem__(self, item):
        result = self.elem.attrib[item]
        return result

    def get(self, item, default=None):
        result = self.elem.attrib.get(item, default)
        return result

    def is_complex(self):
        it = self.elem.iter()
        it.next() # self
        try:
            it.next()
        except StopIteration:
            return False
        return True

    def __repr__(self):
        return "XMLStruct('%s')"%self.elem.tag

    def __str__(self):
        if self.is_complex():
            return "XMLStruct('%s')"%self.elem.tag
        else:
            return self.elem.text

    def __eq__(self, other):
        if isinstance(other, basestring):
            return str(self) == other
        else:
            return self.elem == other.elem

    def __neq__(self, other):
        if isinstance(other, basestring):
            return str(self) != other
        else:
            return self.elem != other.elem
