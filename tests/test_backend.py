"""
Tests for commond Graph manipulations.

Todo - load RDF into base backend to test add/remove features.
"""

from rdflib import URIRef, Graph, RDF, RDFS, Literal
from rdflib.compare import graph_diff

from vdm.backend import BaseBackend
from vdm.namespaces import D, FOAF, VIVO
from vdm.namespaces import ns_mgr

def test_base():
    base = BaseBackend()

    #prop from abbreviation
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


def test_get_subtract_graph():
    g = Graph()
    g.namespace_manager = ns_mgr
    #g.add((D['sample'], RDF.type, FOAF.person))
    g.add((D['sample'], VIVO.overview, Literal("Researcher studying economics.")))
    base = BaseBackend()
    base.graph = g

    trip = {}
    trip['subject'] = D['sample']
    trip['predicate'] = 'vivo:overview'
    trip['object'] = "My new overview"

    remove = base.get_subtract_graph(trip)
    #Subtraction should be equal to the addition.
    #g == remove was not returning True.
    #graph diff was returning prefixes
    assert(
        remove.serialize(format='nt') \
        == \
        g.serialize(format='nt')
    )

def test_create_resource():
    base = BaseBackend()
    name = u"Smith, Sam"
    uri, g = base.create_resource('foaf:Person', name)

    label = g.value(subject=uri, predicate=RDFS.label)
    assert(label.toPython() == name)
    assert(isinstance(uri, URIRef))

    assigned_uri = D['sample']

    uri, g = base.create_resource('foaf:Person', name, uri=assigned_uri)
    assert(uri == assigned_uri)

