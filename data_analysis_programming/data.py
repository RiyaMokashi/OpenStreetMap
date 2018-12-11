#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json
import audit as street_name_auditor

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]

def shape_element(element):
    node = {}
    if element.tag == "node" or element.tag == "way" :
        node["id"] = element.get("id")
        node["type"] = element.tag
        node["visible"] = element.get("visible")
        node["created"] = {
                "version" : element.get("version"),
                "changeset" : element.get("changeset"),
                "timestamp" : element.get("timestamp"),
                "user" : element.get("user"),
                "uid" : element.get("uid")
            }
        if element.get("lat") and element.get("lon"):
            node["pos"] = [float(element.get("lat")), float(element.get("lon"))]
        for child in list(element):
            key_string = child.get("k")
            if key_string:
                keys = process_key_string(key_string)
                node = handle_nested_keys(node, keys, child.get("v"))
            elif element.tag == "way":
                if child.tag == "nd":
                    if "node_refs" in node:
                        node["node_refs"].append(child.get("ref"))
                    else:
                        node["node_refs"] = [child.get("ref")]

        return node
    else:
        return None

def process_key_string(string):
    string = string.replace(' ', '_').replace('.', '_').replace('&', '_and_')
    return string.lower().split(":")

def handle_nested_keys(node, keys, value):
    if len(keys) == 1:
        key, value = process_key_and_value(keys[0], value)
        if value != None:
            node[key] = value
    else:
        key = keys.pop(0)
        if key in node:
            sub_node = node[key]
        else:
            sub_node = {}
        if isinstance(sub_node, dict):
            node[key] = handle_nested_keys(sub_node, keys, value)

    return node

street_name_mapping = [
    {'road': 'Road',
    'way': 'Way',
    'St': 'Street',
    'South 32ed Avenue East': 'South 32nd Avenue East'
    'Ave': 'Avenue'}
]

def process_key_and_value(key, value):
    if key == 'addr':
        key = 'address'
    elif key == 'street':
        value = street_name_auditor.update_name(value, street_name_mapping)
    return key, value

def process_map(file_in, pretty = False):
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data
