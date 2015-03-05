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

def test_make_activity_datetime():
	activity_uri = rdflogger.mint_uuid_uri()
	dt = rdflogger.make_timestamp()
	prov_rdf = rdflogger.make_activity_datetime(activity_uri, dt)
	assert(
		(activity_uri, PROV['startedAtTime'], dt) in prov_rdf
	)
	assert(
		(activity_uri, PROV['endedAtTime'], dt) in prov_rdf
	)

def test_make_prov_object():
	label = 'test activity'
	uri = rdflogger.mint_uuid_uri()
	prov_ob =  rdflogger.make_prov_object(uri, label,'activity')
	assert(
		(uri, RDF['type'], PROV['Activity']) in prov_ob
	)
	assert(
		(uri, RDFS['label'], Literal(label)) in prov_ob
	)

def test_get_prov_class():
	class_string = 'activity'
	prov_class = rdflogger.get_prov_class(class_string)
	assert(
		prov_class == PROV['Activity']
	)
	class_string = 'eNTiTY'
	prov_class = rdflogger.get_prov_class(class_string)
	assert(
		prov_class == PROV['Entity']
	)
	class_string = ' Agent'
	with pytest.raises(KeyError):
		prov_class = rdflogger.get_prov_class(class_string)

def test_make_timestamp():
	tstamp = rdflogger.make_timestamp()
	today_dt = datetime.datetime.today()
	assert(
		type(tstamp) is Literal
	)
	assert(
		tstamp.datatype == XSD['dateTime']
	)
	dt = tstamp.toPython()
	assert(
		dt.year == today_dt.year
	)
	assert(
		dt.day == today_dt.day
	)

def test_make_statement_rdf():
	#Eventually, need a function to decompose RDF and rdflib triples
	#into s,p,o
	s = URIRef('subject')
	p = URIRef('predicate')
	o = URIRef('object')
	action = Literal('add')
	stmt = rdflogger.mint_uuid_uri()
	activity = rdflogger.mint_uuid_uri()
	stmt_prov = rdflogger.make_statement_rdf(stmt,activity,action,s,p,o)
	assert(
		(stmt, RDF['type'], RDF['Statement']) in stmt_prov
	)
	assert(
		(stmt, RDF['subject'], s) in stmt_prov
	)
	assert(
		(stmt, RDF['predicate'], p) in stmt_prov
	)
	assert(
		(stmt, RDF['object'], o) in stmt_prov
	)
	assert(
		(stmt, BPROV['action'], action) in stmt_prov
	)
	assert(
		(stmt, BPROV['statmentGeneratedBy'], activity) in stmt_prov
	)
	assert(
		(activity, BPROV['generatedStatement'], stmt) in stmt_prov
	)
	assert(
		len(stmt_prov) == 7
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