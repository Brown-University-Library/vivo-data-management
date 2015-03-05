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

import rdflog

PROV = Namespace('http://www.w3.org/ns/prov#')
BPROV = Namespace('http://vivo.brown.edu/ontology/provenance#')


# def test_log_prov():
# 	log_rdf = log_prov(action, triples)
# 	in_g = Graph()
# 	out_g = Graph()
# 	stmts = [
# 		(D['n59033'], BCITE['date'], Literal('1985-06-01')),
# 		(D['n59033'], BCITE['publishedIn'],
# 				Literal('Trends in Biochemical Sciences')),
# 		(D['n51534'], BCITE['issn'], Literal('0968-0004')),
# 		(D['n59033'], BCITE['volume'], Literal('10'))
# 	]
# 	for s in stmts:
# 		in_g.add(s)

# 	actv = rdflog.mint_uuid_uri()
# 	actv_obj = rdflog.make_prov_object(
# 		actv, 'CrossRefDOIHarvest', 'activity'
# 		)
# 	out_g += actv_obj
# 	dt = rdflog.make_timestamp()
# 	activity_rdf = rdflog.make_activity_rdf(actv, dt)
# 	out_g += activity_rdf
# 	for s,p,o in in_g.triples(None,None,None):
# 		stmt = rdflog.mint_uuid_uri()
# 		stmt_rdf = rdflog.make_statement_rdf(
# 			stmt,actv,'add',s,p,o
# 			)
# 		out_g += stmt_rdf

def test_make_activity_rdf():
	activity_uri = rdflog.mint_uuid_uri()
	dt = rdflog.make_timestamp()
	prov_rdf = rdflog.make_activity_rdf(activity_uri, dt)
	assert(
		(activity_uri, PROV['startedAtTime'], dt) in prov_rdf
	)
	assert(
		(activity_uri, PROV['endedAtTime'], dt) in prov_rdf
	)
	agent_uri = rdflog.mint_uuid_uri()
	source_uri = rdflog.mint_uuid_uri()
	prov_rdf = rdflog.make_activity_rdf(
		activity_uri, dt, agent=agent_uri, source=source_uri
		)
	assert(
		(activity_uri, PROV['wasAssociatedWith'], agent_uri)
			in prov_rdf
	)
	assert(
		(activity_uri, PROV['used'], source_uri) in prov_rdf
	)

def test_make_prov_object():
	label = 'test activity'
	uri = rdflog.mint_uuid_uri()
	prov_ob =  rdflog.make_prov_object(uri, label,'activity')
	assert(
		(uri, RDF['type'], PROV['Activity']) in prov_ob
	)
	assert(
		(uri, RDFS['label'], Literal(label)) in prov_ob
	)

def test_get_prov_class():
	class_string = 'activity'
	prov_class = rdflog.get_prov_class(class_string)
	assert(
		prov_class == PROV['Activity']
	)
	class_string = 'eNTiTY'
	prov_class = rdflog.get_prov_class(class_string)
	assert(
		prov_class == PROV['Entity']
	)
	class_string = ' Agent'
	with pytest.raises(KeyError):
		prov_class = rdflog.get_prov_class(class_string)

def test_make_timestamp():
	tstamp = rdflog.make_timestamp()
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
	label = Literal('{0} {1} {2}'.format(s,p,o)) #candidate for serialize?
	stmt = rdflog.mint_uuid_uri()
	activity = rdflog.mint_uuid_uri()
	stmt_prov = rdflog.make_statement_rdf(stmt,activity,action,s,p,o)
	assert(
		(stmt, RDF['type'], RDF['Statement']) in stmt_prov
	)
	assert(
		(stmt, RDFS['label'], label) in stmt_prov
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
		len(stmt_prov) == 8
	)

def test_mint_uuid_uri():
	uri = rdflog.mint_uuid_uri()
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