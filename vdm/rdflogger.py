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
	activity_class = activity_map[activty]
	return activity_class

class RDFLogger(object):
	def __init__(self, activity_class=None):
		self.logger = logger
		self.activity_uri = ''
		self.add_triples = Graph()
		self.remove_triples = Graph()
		self.graph = Graph()
		self.add_activity(activity_class)

	def add_activity(self, activity_class=None):
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
		self.add_triples += graph

	def remove_rdf(self, graph):
		self.remove_triples += graph

	def log(self):
		self.graph_statements()
		nt = self.graph.serialize(format='nt')
		self.logger.warning(nt)

	def graph_statements(self):
		for s,p,o in self.add_triples.triples((None,None,None)):
			action = BPROV['Add']
			self.add_statement(action,s,p,o)
		for s,p,o in self.remove_triples.triples((None,None,None)):
			action = BPROV['Remove']
			self.add_statement(action,s,p,o)

	def add_statement(self,action,s,p,o):
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
    ####### Functions  ######
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

	#def add_user_agent(self, shortid):


# class CRHLogger(ActivityLogger):
# 	"""
# 	CrossRefHarvestLogger
# 	Logs RDF produced by harvesting metadata from CrossRef
# 	"""
# 	def __init__(self):
# 		super(CRHLogger, self).__init__()
# 		self.label = 'CrossRef DOI Harvest'
# 		self.entities = ['http://search.crossref.org/']

# class PMHLogger(ActivityLogger):
# 	"""
# 	PubMed HarvestLogger
# 	Logs RDF produced by harvesting metadata from PubMed
# 	"""
# 	def __init__(self):
# 		super(PMHLogger, self).__init__()
# 		self.label = 'PubMed PMID Harvest'
# 		self.entities = ['http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=%s&retmode=json']

# class VMLogger(ActivityLogger):
# 	"""
# 	VIVOManagerLogger
# 	Logs RDF produced by edits made via VIVO Manager
# 	"""
# 	def __init__(self):
# 		super(VMLogger, self).__init__()
# 		self.label = 'VIVO Manager Logger'

# 	def add_faculty_agent(self, shortid):
# 		self.agents.append(shortid)

# class FISLogger(ActivityLogger):
# 	def __init__(self):
# 		super(FISLogger, self).__init__()
# 		self.activity_subclass = BPROV['FISFacultyFeed']