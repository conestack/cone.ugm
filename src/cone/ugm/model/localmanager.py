import os
import types
from lxml import etree
from plumber import (
    plumber,
    finalize,
)
from node.parts import (
    Nodify,
    DictStorage,
)


class LocalManagerConfig(DictStorage):
    """Local Management configuration storage.
    """
    
    @finalize
    def load(self):
        path = self.file_path
        if not path or not os.path.exists(path):
            return
        with open(path, 'r') as handle:
            tree = etree.parse(handle)
        root = tree.getroot()
        for rule in root.getchildren():
            new_rule = self.storage[rule.tag] = dict()
            for prop in rule.getchildren():
                for tag_name in ['target', 'default']:
                    if prop.tag == tag_name:
                        new_rule[tag_name] = list()
                        for group in prop.getchildren():
                            new_rule[tag_name].append(group.text)
    
    @finalize
    def __call__(self):
        root = etree.Element('localmanager')
        for gid, rule in self.storage.items():
            group = etree.SubElement(root, gid)
            for tag_name in ['target', 'default']:
                elem = etree.SubElement(group, tag_name)
                for gid in rule[tag_name]:
                    item = etree.SubElement(elem, 'item')
                    item.text = gid
        with open(self.file_path, 'w') as handle:
            handle.write(etree.tostring(root, pretty_print=True))


class LocalManagerConfigAttributes(object):
    __metaclass__ = plumber
    __plumbing__ = (
        Nodify,
        LocalManagerConfig,
    )
    
    def __init__(self, path):
        self.file_path = path
        self.load()