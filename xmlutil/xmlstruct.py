import xml.etree.cElementTree as ET

autoint = True

class XMLStruct(object):

    def __init__(self, arg):
        if isinstance(arg, basestring):
            if '<' in arg:
                # XML text
                self.elem = ET.fromstring(arg)
            else:
                # XML file name
                self.elem = ET.parse(arg).getroot()
        else:
            self.elem = arg
    
    def __getattr__(self, attr):
        elem = self.elem.find(attr)
        result = as_struct(elem)
        if result is None and attr == 'text':
            return self.elem.text
        return result

    def __getitem__(self, item):
        if isinstance(item, int):
            # List-like access
            return as_struct(self.elem[item])
        result = self.elem.get(item)
        return result

    def get(self, item, default=None):
        result = self.elem.attrib.get(item, default)
        return result

    def __len__(self):
        return len(self.elem)

    def __repr__(self):
        s_attr = ''.join(", %s='%s'"%(k, v) for k,v in self.elem.items())
        return "XMLStruct('%s'%s)"%(self.elem.tag, s_attr)

    def __str__(self):
        if is_complex(self.elem):
            return self.__repr__()
        else:
            return self.elem.text

    def __call__(self, match, **kwargs):
        """
        Find first element by tag name or path, filtering by given attributes
        """
        for e in self.elem.iterfind(match):
            mismatch = any([e.get(k) != v for k, v in kwargs.iteritems()])
            if not mismatch:
                return as_struct(e)
        return None

def is_complex(elem):
    if elem.keys():
        # has attributes
        return True
    # check if has children
    it = elem.iter()
    it.next() # self
    try:
        it.next()
    except StopIteration:
        return False
    return True

def as_struct(elem):
    """
    Returns a simple int / string for simple elements,
    and XMLStruct() representation for complex ones.
    Need better name for this method?
    """
    if elem is None:
        return None
    if is_complex(elem):
        return XMLStruct(elem)
    if autoint:
        if elem.text.lower().startswith('0x'):
            return int(elem.text[2:], 16)
        try:
            return int(elem.text)
        except ValueError:
            pass
    return elem.text
