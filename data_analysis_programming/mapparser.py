#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import pprint

def count_tags(filename):
    tags = {}
    tree = ET.parse(filename)
    for el in tree.iter():
        if el.tag in tags:
            tags[el.tag] += 1
        else:
            tags[el.tag] = 1
    return tags

def test():

    tags = count_tags('duluth.osm_01.osm')
    pprint.pprint(tags)
    assert tags == {'bounds': 1,
                     'member': 3,
                     'nd': 4,
                     'node': 20,
                     'osm': 1,
                     'relation': 1,
                     'tag': 7,
                     'way': 1}



if __name__ == "__main__":
    test()
