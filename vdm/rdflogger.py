import logging
import traceback
import uuid
import datetime

from rdflib import RDF, RDFS, URIRef, Namespace, XSD, Literal
from rdflib import Graph

from vdm.namespaces import D, BCITE

PROV = Namespace('http://www.w3.org/ns/prov#')
BPROV = Namespace('http://vivo.brown.edu/ontology/provenance#')

logger = logging.getLogger('rdflog')
logger.setLevel(11)
# This must be an absolute path
fh = logging.FileHandler('/work/staging/rdflog.nt')
logger.addHandler(fh)
logger.propagate = False

def mint_uuid_uri():
	unique = 'n' + uuid.uuid4().hex
	uri = D[unique]
	return uri

def make_timestamp():
	dt = datetime.datetime.utcnow()
	tstamp = Literal(dt,datatype=XSD.dateTime)
	return tstamp

def make_prov_object(uri, label, prov_class):
	label_literal = Literal(label)
	prov_type = get_prov_class(prov_class)
	g = Graph()
	triples = [
		(uri, RDF['type'], prov_type),
		(uri, RDFS['label'], label_literal),
	]
	for t in triples:
		g.add(t)
	return g

def get_prov_class(class_string):
	class_string = class_string.lower()
	class_map = {
		'activity': PROV['Activity'],
		'entity': PROV['Entity'],
		'agent': PROV['Agent']
	}
	try:
		obj_type = class_map[class_string]
	except KeyError:
		raise
	return obj_type

def make_activity_datetime(actv_uri, datetime):
	g = Graph()
	triples = [
		(actv_uri, PROV['startedAtTime'], datetime),
		(actv_uri, PROV['endedAtTime'], datetime),
	]
	for t in triples:
		g.add(t)
	return g

def make_statement_rdf(stmt_uri,activity_uri,action,s,p,o):
	g = Graph()
	triples = [
		(stmt_uri, RDF['type'], RDF['Statement']),
		(stmt_uri, BPROV['action'], action),
		(stmt_uri, BPROV['statmentGeneratedBy'], activity_uri),
		(activity_uri, BPROV['generatedStatement'], stmt_uri),
		(stmt_uri, RDF['subject'], s),
		(stmt_uri, RDF['predicate'], p),
		(stmt_uri, RDF['object'], o)
	]
	for t in triples:
		g.add(t)
	return g


class ActivityLogger(object):
	def __init__(self):
		self.label = 'Activity'
		self.logger = logger
		self.activity_uri = mint_uuid_uri()
		self.entities = []
		self.agents = []
		self.add_triples = Graph()
		self.remove_triples = Graph()
		self.graph = Graph()

	def add_rdf(self, graph):
		self.add_triples += graph

	def remove_rdf(self, graph):
		self.remove_triples += graph

	def add_software_agent(self):
		#consider also LogRecord.pathname
		#Need custom Handler
		stack = traceback.extract_stack(limit=2)[0]
		swAgent = 'Func: {2} File: {0} Line: {1}'.format(*stack)
		self.agents.append(swAgent)

	def graph_activity(self):
		activity_rdf = make_prov_object(
			self.activity_uri, self.label, 'activity'
			)
		dt = make_timestamp()
		dt_rdf = make_activity_datetime(self.activity_uri, dt)
		self.graph += activity_rdf
		self.graph += dt_rdf

	def graph_agents(self):
		for agent in self.agents:
			uri = mint_uuid_uri()
			agent_rdf = make_prov_object(uri, agent, 'agent')
			activity_rdf = (self.activity_uri, PROV['wasAssociatedWith'], uri)
			self.graph.add(activity_rdf)
			self.graph += agent_rdf

	def graph_entities(self):
		for entity in self.entities:
			uri = mint_uuid_uri()
			entity_rdf = make_prov_object(uri, entity, 'entity')
			activity_rdf = (self.activity_uri, PROV['used'], uri)
			self.graph.add(activity_rdf)
			self.graph += entity_rdf

	def graph_statements(self):
		for s,p,o in self.add_triples.triples((None,None,None)):
			stmt = mint_uuid_uri()
			action = D['bprov-Add']
			stmt_rdf = make_statement_rdf(
				stmt,self.activity_uri,action,s,p,o
				)
			self.graph += stmt_rdf
		for s,p,o in self.remove_triples.triples((None,None,None)):
			stmt = mint_uuid_uri()
			action = D['bprov-Remove']
			stmt_rdf = make_statement_rdf(
				stmt,self.activity_uri,action,s,p,o
				)
			self.graph += stmt_rdf

	def log(self):
		self.graph_activity()
		self.graph_agents()
		self.graph_entities()
		self.graph_statements()
		nt = self.graph.serialize(format='nt')
		self.logger.warning(nt)

class CRHLogger(ActivityLogger):
	"""
	CrossRefHarvestLogger
	Logs RDF produced by harvesting metadata from CrossRef
	"""
	def __init__(self):
		super(CRHLogger, self).__init__()
		self.label = 'CrossRef DOI Harvest'
		self.entities = ['http://search.crossref.org/']

class PMHLogger(ActivityLogger):
	"""
	PubMed HarvestLogger
	Logs RDF produced by harvesting metadata from PubMed
	"""
	def __init__(self):
		super(PMHLogger, self).__init__()
		self.label = 'PubMed PMID Harvest'
		self.entities = ['http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=%s&retmode=json']

class VMLogger(ActivityLogger):
	"""
	VIVOManagerLogger
	Logs RDF produced by edits made via VIVO Manager
	"""
	def __init__(self):
		super(VMLogger, self).__init__()
		self.label = 'VIVO Manger Logger'

	def add_faculty_agent(self, shortid):
		self.agents.append(shortid)