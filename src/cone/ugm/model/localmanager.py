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
                if prop.tag == 'target':
                    new_rule['target'] = list()
                    for group in prop.getchildren():
                        new_rule['target'].append(group.text)
                if prop.tag == 'default':
                    new_rule['default'] = prop.text
    
    @finalize
    def __call__(self):
        root = etree.Element('localmanager')
        for gid, rule in self.storage.items():
            group = etree.SubElement(root, gid)
            target = etree.SubElement(group, 'target')
            for target_gid in rule['target']:
                item = etree.SubElement(target, 'item')
                item.text = target_gid
            default = etree.SubElement(group, 'default')
            default.text = rule['default']
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