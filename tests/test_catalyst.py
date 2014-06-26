
from vdm.catalyst import DisambiguationEngine

def pretty(raw):
    """
    Pretty print xml.
    """
    import xml.dom.minidom
    xml = xml.dom.minidom.parseString(raw)
    pretty = xml.toprettyxml()
    return pretty


def test_profile():
    #Basic info about a person.
    p = [
        'Josiah',
        'Carberry',
        None,
        'jcarberry@brown.edu',
        ['null'],
        ['null']
    ]

    disambig = DisambiguationEngine()
    disambig.affiliation_strings = ['Sample University']

    doc = disambig.build_doc(*p)

    #Basic verification that XML contains what we expect.
    assert('<First>Josiah</First>' in doc)
    assert('<Last>Carberry</Last>' in doc)
    assert('<email>jcarberry@brown.edu</email>' in doc)
    assert('<Affiliation>%Sample University%</Affiliation>' in doc)
