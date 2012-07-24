import os
import types
from lxml import etree


class LocalManagerConfig(object):
    """Local Management configuration.
    """
    
    def __init__(self, path):
        self.path = path
        self.rules = dict()
        if not path or not os.path.exists(path):
            return
        with open(path, 'r') as handle:
            tree = etree.parse(handle)
        root = tree.getroot()
        for rule in root.getchildren():
            new_rule = self.rules[rule.tag] = dict()
            for prop in rule.getchildren():
                if prop.tag == 'target':
                    new_rule['target'] = list()
                    for group in prop.getchildren():
                        new_rule['target'].append(group.text)
                if prop.tag == 'default':
                    new_rule['default'] = prop.text
    
    def __getitem__(self, key):
        return self.rules[key]
    
    def __setitem__(self, key, val):
        self.rules[key] = val
    
    def __delitem__(self, key):
        del self.rules[key]
    
    def __iter__(self):
        return self.rules.__iter__()
    
    def get(self, key, default=None):
        return self.get(key, default)
    
    def keys(self):
        return self.rules.keys()
    
    def values(self):
        return self.rules.values()
    
    def items(self):
        return self.rules.items()
    
    def __call__(self):
        root = etree.Element('localmanager')
        for gid, rule in self.rules.items():
            group = etree.SubElement(root, gid)
            target = etree.SubElement(group, 'target')
            for target_gid in rule['target']:
                item = etree.SubElement(target, 'item')
                item.text = target_gid
            default = etree.SubElement(group, 'default')
            default.text = rule['default']
        with open(self.path, 'w') as handle:
            handle.write(etree.tostring(root, pretty_print=True))