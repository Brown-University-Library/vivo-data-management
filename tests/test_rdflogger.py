import pytest
# import os
import uuid
import datetime
import re
# import rdflib
from rdflib import RDF, RDFS, URIRef, Namespace, XSD, Literal
from rdflib import Graph

# from vdm import namespaces
# from vdm.namespaces import D, RDFS

import vdm.rdflogger as rdflogger

PROV = Namespace('http://www.w3.org/ns/prov#')
BPROV = Namespace('http://vivo.brown.edu/ontology/provenance#')


def test_instantiate_Activity():
	act1 = rdflogger.ActivityRDF()
	assert(
		hasattr(act1, 'activity_uri')
	)
	assert(
		hasattr(act1, 'graph')
	)
	uri = act1.activity_uri
	graph = act1.graph
	assert(
		(uri, RDF['type'], PROV['Activity']) in graph
	)
	assert(
		(uri, PROV['startedAtTime'], None) in graph
	)
	assert(
		(uri, PROV['endedAtTime'], None) in graph
	)
	assert(
		(uri, RDFS['label'], None) in graph
	)
	assert(
		len(graph) == 4
	)

def test_instantiate_typed_activity():
	act1 = rdflogger.ActivityRDF('BannerFeed')
	uri = act1.activity_uri
	graph = act1.graph
	assert(
		(uri, RDF['type'], BPROV['BannerFeed']) in graph
	)

def test_bad_activity_type_fails():
	with pytest.raises(KeyError):
		act1 = rdflogger.ActivityRDF('FakeFeed')

def test_graph_statements():
	act1 = rdflogger.ActivityRDF()
	s = URIRef('http://example.com/fake')
	p = RDFS['label']
	o = Literal('fake')
	action = BPROV['Add']
	act1.graph_statements(action,s,p,o)
	activity = act1.activity_uri
	graph = act1.graph
	assert(
		(None, RDF['type'], RDF['Statement']) in graph
	)
	assert(
		(None, RDF['subject'], s) in graph
	)
	assert(
		(None, RDF['predicate'], p) in graph
	)
	assert(
		(None, RDF['object'], o) in graph
	)
	assert(
		(None, BPROV['action'], action) in graph
	)
	assert(
		(None, BPROV['statmentGeneratedBy'], activity) in graph
	)
	assert(
		(activity, BPROV['generatedStatement'], None) in graph
	)

def test_add_rdf():
	add = Graph()
	stmts = [
		(URIRef('http://example.com/fake'),
			RDFS['label'], Literal('fake')),
		(URIRef('http://example.com/fake'),
			RDF['type'], BPROV['FakeClass'])
		]
	for s in stmts:
		add.add(s)
	act1 = rdflogger.ActivityRDF()
	act1.add_rdf(add)
	graph = act1.graph
	assert(
		(None, BPROV['action'], BPROV['Add']) in graph
	)
	assert(
		(None, RDF['subject'], URIRef('http://example.com/fake'))
			in graph
	)
	assert(
		(None, RDF['object'], Literal('fake')) in graph
	)
	assert(
		(None, RDF['object'], BPROV['FakeClass']) in graph
	)
	# Counting the number of triples with the type 'Statement'
	# (counting length of generator output)
	# http://stackoverflow.com/questions/393053/length-of-generator-output
	assert(
		sum(1 for _ in graph.triples(
			(None, RDF['type'], RDF['Statement'])
			)) == 2
	)

def test_remove_rdf():
	rmv = Graph()
	stmts = [
		(URIRef('http://example.com/fake'),
			RDFS['label'], Literal('fake')),
		(URIRef('http://example.com/fake'),
			RDF['type'], BPROV['FakeClass'])
		]
	for s in stmts:
		rmv.add(s)
	act1 = rdflogger.ActivityRDF()
	act1.remove_rdf(rmv)
	graph = act1.graph
	uri = act1.activity_uri
	assert(
		(None, BPROV['action'], BPROV['Remove']) in graph
	)
	assert(
		(uri, BPROV['generatedStatement'], None) in graph
	)
	# Counting the number of triples with the type 'Statement'
	# (counting length of generator output)
	# http://stackoverflow.com/questions/393053/length-of-generator-output
	assert(
		sum(1 for _ in graph.triples(
			(None, RDF['type'], RDF['Statement'])
			)) == 2
	)

def test_make_timestamp():
	tstamp = rdflogger.make_timestamp()
	now_dt = datetime.datetime.utcnow()
	assert(
		type(tstamp) is Literal
	)
	assert(
		tstamp.datatype == XSD['dateTime']
	)
	dt = tstamp.toPython()
	assert(
		dt.year == now_dt.year
	)
	assert(
		dt.day == now_dt.day
	)

def test_mint_uuid_uri():
	uri = rdflogger.mint_uuid_uri()
	assert(
		type(uri) is URIRef
	)
	uri_val = uri.n3()
	uri_regex = re.compile(
		"<http://vivo.brown.edu/individual/n[a-z0-9]{32}>"
		)
	assert(
		uri_regex.match(uri_val)
	)