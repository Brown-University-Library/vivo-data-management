import logging
import traceback
import uuid
import datetime

from rdflib import RDF, RDFS, URIRef, Namespace, XSD, Literal
from rdflib import Graph
from rdflib.resource import Resource

from vdm.namespaces import D, BCITE

PROV = Namespace('http://www.w3.org/ns/prov#')
BPROV = Namespace('http://vivo.brown.edu/ontology/provenance#')

logger = logging.getLogger('rdflog')
logger.setLevel(11)
# This must be an absolute path
today = datetime.date.today()
fname = 'rdflog.{0}.nt'.format(today.isoformat())
path = '/work/staging/test-logs/' + fname
fh = logging.FileHandler(path)
logger.addHandler(fh)
logger.propagate = False

activity_map = {
	'FISFacultyFeed': BPROV['FISFacultyFeed'],
	'FISAppointmentsFeed': BPROV['FISAppointmentsFeed'],
	'FISDegreesFeed': BPROV['FISDegreesFeed'],
	'BannerFeed': BPROV['BannerFeed'],
	'CrossRefHarvest': BPROV['CrossRefHarvest'],
	'VIVOManagerEdit': BPROV['VIVOManagerEdit'],
	'PubMedHarvest': BPROV['PubMedHarvest'],
}

def mint_uuid_uri():
	unique = 'n' + uuid.uuid4().hex
	uri = D[unique]
	return uri

def make_timestamp():
	dt = datetime.datetime.utcnow()
	tstamp = Literal(dt,datatype=XSD.dateTime)
	return tstamp

def lookup_activity_class(activty):
	try:
		activity_class = activity_map[activty]
		return activity_class
	except KeyError:
		raise KeyError('unrecognized Activity subclass')

class RDFLogger(object):
	def __init__(self):
		self.logger = logger
		self.graph = Graph()

	def add_rdf(self, rdf_object):
		self.graph += rdf_object.graph

	def log(self):
		nt = self.graph.serialize(format='nt')
		self.logger.warning(nt)

class ActivityRDF(object):
	def __init__(self, activity_class=None):
		self.activity_uri = ''
		self.graph = Graph()
		self.graph_activity(activity_class)

	def graph_activity(self, activity_class=None):
		uri = mint_uuid_uri()
		activity_res = Resource(self.graph, uri)
		self.activity_uri = uri
		activity_res.add(RDF['type'], PROV['Activity'])
		dt = make_timestamp()
		activity_res.add(PROV['startedAtTime'], dt)
		activity_res.add(PROV['endedAtTime'], dt)
		if activity_class:
			subclass = lookup_activity_class(activity_class)
			activity_res.add(RDF['type'], subclass)
			activity_label = activity_class
		else:
			activity_label = 'Activity'
		activity_label += ': {0}'.format(dt)
		activity_res.add(RDFS['label'], Literal(activity_label))

	def add_rdf(self, graph):
		for s,p,o in graph.triples((None,None,None)):
			action = BPROV['Add']
			self.graph_statements(action,s,p,o)

	def remove_rdf(self, graph):
		for s,p,o in graph.triples((None,None,None)):
			action = BPROV['Remove']
			self.graph_statements(action,s,p,o)

	def stage(self, add=None, remove=None):
		if add:
			self.add_rdf(add)
		if remove:
			self.remove_rdf(remove)

	def graph_statements(self,action,s,p,o):
		uri = mint_uuid_uri()
		stmt_res = Resource(self.graph, uri)
		stmt_res.add(RDF['type'], RDF['Statement'])
		stmt_res.add(BPROV['action'], action)
		stmt_res.add(BPROV['statmentGeneratedBy'], self.activity_uri)
		stmt_res.add(RDF['subject'], s)
		stmt_res.add(RDF['predicate'], p)
		stmt_res.add(RDF['object'], o)
		self.graph.add(
			(self.activity_uri, BPROV['generatedStatement'], uri)
			)

	#########################
	###### Convenience ######
    ####### Functions #######
    #########################

	def add_source(self, source):
		uri = mint_uuid_uri()
		src_res = Resource(self.graph, uri)
		src_res.add(RDF['type'], PROV['Entity'])
		src_res.add(RDFS['label'], Literal(source))
		self.graph.add(
			(self.activity_uri, PROV['used'], uri)
			)

	def add_software_agent(self):
		#consider also LogRecord.pathname
		#Need custom Handler
		stack = traceback.extract_stack(limit=2)[0]
		sw_label = 'Func: {2} File: {0} Line: {1}'.format(*stack)
		uri = mint_uuid_uri()
		sw_res = Resource(self.graph, uri)
		sw_res.add(RDF['type'], PROV['SoftwareAgent'])
		sw_res.add(RDFS['label'], Literal(sw_label))
		self.graph.add(
			(self.activity_uri, PROV['wasAssociatedWith'], uri)
			)

	def add_user_agent(self, agent_uri):
		#expects a URI as agent_uri
		if not isinstance(agent_uri, URIRef):
			raise TypeError('Expecting User URI')
		agent_res = Resource(self.graph, agent_uri)
		agent_res.add(RDF['type'], PROV['Agent'])
		agent_res.add(RDFS['label'], Literal(agent_uri))
		self.graph.add(
			(self.activity_uri, PROV['wasAssociatedWith'], agent_uri)
			)