import re
import xml.etree.cElementTree as ET

# Automatically convert string to integers, when possible
autoint = True

# Allow access to tag attributes with '.xxx' (in addition to '["xxx"]')
get_attr_as_member = True

class XMLStruct(object):

    def __init__(self, arg, **kwargs):
        if isinstance(arg, basestring):
            if '<' in arg:
                # XML text
                self.elem = ET.fromstring(arg)
            elif arg.lower().endswith('.xml'):
                # XML file name
                self.elem = ET.parse(arg).getroot()
            else:
                # Top element
                attr = ''.join([' %s="%s"'%(k, v) for k,v in sorted(kwargs.iteritems())])
                self.elem = ET.fromstring("<%s%s></%s>"%(arg, attr, arg))
        else:
            self.elem = arg
        self._by_key = {}
    
    def __getattr__(self, attr):
        if attr in self.__dict__:
            return self.__dict__[attr]
        elem = self.elem.find(attr)
        result = as_struct(elem)
        if result is None and attr in ('text', 'tag'):
            result = getattr(self.elem, attr)
        elif get_attr_as_member and attr in self.elem.attrib:
            result = self[attr]
        self.__dict__[attr] = result # must cache, so that user can refer to same object later
        return result

    def __setattr__(self, attr, value):
        if isinstance(value, basestring) or isinstance(value, int):
            child = getattr(self, attr)
            # If there exists a child with a name of a given attribute,
            # set its text to a given value
            if child:
                child.elem.text = unicode(value)
                return
        self.__dict__[attr] = value

    def __getitem__(self, item):
        if isinstance(item, int):
            # List-like access
            return as_struct(self.elem[item])
        s = self.elem.get(item)
        return try_str2int(s)

    def __setitem__(self, item, value):
        self.elem.attrib[item] = value

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

    def __eq__(self, other):
        diff = self.is_different(other)
        return not diff

    def __ne__(self, other):
        diff = self.is_different(other)
        return diff

    #def append(self, _tag, *args, **kwargs):
    #    # args[0] - element text (optional)
    #    # kwargs - element attributes
    #    attr = ''.join([' %s="%s"'%(k, v) for k,v in sorted(kwargs.iteritems())])
    #    if len(args) > 0:
    #        text = args[0]
    #    else:
    #        text = ''
    #    s = '<%s%s>%s</%s>'%(_tag, attr, text, _tag)
    #    e = ET.fromstring(s)
    #    print "CREATE", s, e.text
    #    self.elem.append(e)
    #    print "XXX", self(_tag, **kwargs)

    def is_different(self, other, recheck=None):
        if isinstance(other, basestring):
            if other is None: other = ""
            text = self.text
            if text is None: text = ""
            if text != other:
                if not recheck or recheck(self, other):
                    return True
            return False
        if self.elem.tag != other.elem.tag or \
           self.elem.attrib != other.elem.attrib or \
           self.elem.text != other.elem.text or \
           len(self) != len(other):
            if not recheck or recheck(self, other):
                return True
        a1 = list(self)
        a2 = list(other)
        for i, e1 in enumerate(a1):
            e2 = a2[i]
            if e1 == e2: continue
            if not hasattr(e1, 'is_different') or e1.is_different(e2):
                return True
        return False

    def as_dict(self, key):
        if key in self._by_key:
            return self._by_key[key]
        ans = {}
        for e in self:
            if key in e.elem.attrib:
                ans[e[key]] = e
            elif hasattr(e, key):
                ans[getattr(e, key)] = e
            else:
                raise KeyError("Attribute or tag '%s' not found in %s"%(key, e))
        self._by_key[key] = ans
        return ans

    def dumps(self, indent=2, level=0):
        if level == 0:
            ans = u'<?xml version="1.0" encoding="UTF-8"?>\n'
        else:
            ans = u''
        pre = ' ' * indent * level
        attr = ''.join([' %s="%s"'%(k, v) for k,v in sorted(self.elem.items())])
        ans += pre + '<%s%s>\n'%(self.tag, attr)
        for e in self:
            ans += e.dumps(indent=indent, level=level+1)
        ans += pre + '</%s>\n'%self.tag
        return ans

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

class xInt(long):
    def dumps(self, indent=2, level=0):
        pre = u' ' * indent * level
        return pre + '<%s>%s</%s>\n'%(self.tag, self, self.tag)

class xStr(unicode):
    def dumps(self, indent=2, level=0):
        pre = u' ' * indent * level
        s, n = re.subn(r'(?m)^', pre, self)
        if n > 1:
            return u"%s<%s>\n%s\n%s</%s>\n"%(pre, self.tag, s, pre, self.tag)
        else:
            return u"%s<%s>%s</%s>\n"%(pre, self.tag, self, self.tag)

def try_str2int(s):
    if not autoint or s is None: return s
    try:
        if s.lower().startswith('0x'):
            return xInt(s[2:], 16)
        else:
            return xInt(s)
    except ValueError:
        pass
    return s

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
    ans = try_str2int(elem.text)
    if isinstance(ans, basestring) or ans is None:
        ans = xStr(elem.text if elem.text else "")
    ans.tag = elem.tag
    ans.elem = elem
    return ans
