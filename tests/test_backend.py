"""
Tests for commond Graph manipulations.

Todo - load RDF into base backend to test add/remove features.
"""

from rdflib import URIRef, Graph, RDF

from vdm.backend import BaseBackend
from vdm.namespaces import D, FOAF, VIVO

def test_base():
    base = BaseBackend()

    prop = base.get_prop_from_abbrv('vivo:overview')
    assert(prop == VIVO['overview'])

    #uuid
    uuid_uri = base.uuid_uri()
    assert(isinstance(uuid_uri, URIRef))
    assert(type(uuid_uri) != str)
    assert(type((uuid_uri) != unicode))
    assert(base.local_name(uuid_uri).startswith('n'))
    uuid2 = base.uuid_uri(prefix='q')
    ln = base.local_name(uuid2)
    assert(ln.startswith('q'))

    #local name
    assert(base.local_name(D['jjones']) == 'jjones')
    assert(base.local_name(D['n1234']) == 'n1234')
    assert(base.local_name(D['q1234']) == 'q1234')


def test_base_create_resource():
    base = BaseBackend()
    #create resource
    uri, g = base.create_resource('foaf:Person', "Jeff Jones")
    rtype = g.value(subject=uri, predicate=RDF.type)
    assert(rtype == FOAF.Person)

    uri, g = base.create_resource('vivo:InformationResource', "My Book", uri=D['p1234'])
    assert(uri == D['p1234'])
    rtype = g.value(subject=uri, predicate=RDF.type)
    assert(rtype == VIVO.InformationResource)
