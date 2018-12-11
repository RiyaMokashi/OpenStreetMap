
import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

OSMFILE = "duluthsuperior.osm_01.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road",
            "Trail", "Parkway"]

# UPDATE THIS VARIABLE
ordered_mappings = [
    {".": ""},
    {"St": "Street",
    "Ave": "Avenue",
    "Rd": "Road"}
]


def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)


def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    return street_types

def update_name(name, ordered_mappings):
    for mapping in ordered_mappings:
        for old, new, in mapping.iteritems():
            if name[-len(old):] == old:
                name = name[:-len(old)] + new

    if name == '':
        return None
    return name


def test():
    st_types = audit(OSMFILE)
    assert len(st_types) == 3
    pprint.pprint(dict(st_types))

    for st_type, ways in st_types.iteritems():
        for name in ways:
            better_name = update_name(name, ordered_mappings)
            print name, "=>", better_name
            if name == "W 2nd St.":
                assert better_name == "West Second Street"
            if name == "Haines Rd.":
                assert better_name == "Haines Road"


if __name__ == '__main__':
    test()
