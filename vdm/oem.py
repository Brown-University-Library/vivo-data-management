'''
############
##Sketches##
############

class Attribute(object):
	def __init__(self):
		self.uri = uri
		self.label = label

class Entity(object):
	def __init__(self):
		self.uri = uri
		self.label = label
		self.class = [OWLthing(), *RDFclass]
		self.properties = [RDFlabel, RDFStype, ]

class RDFclass(Entity):
	def __init__(self):
		self.uri = uri
		self.label = label
		self.superclass = list(RDFClass)

class PROVactivity(Entity):
	def __init__(self):
		self.uri = uri
		self.label = label
		self.class = list(RDFClass)
		self.properties = list(RDFProperty)
		for p in self.properties:
			self.p = list(objects)

class PROVentity(Entity):
	def __init__(self):
		self.uri = uri
		self.label = label
		self.class = list(RDFClass)
		self.properties = list(RDFProperty)
		for p in self.properties:
			self.p = list(objects)

class PROVagent(Entity):
	def __init__(self):
		self.uri = uri
		self.label = label
		self.class = list(RDFClass)
		self.properties = list(RDFProperty)
		for p in self.properties:
			self.p = list(objects)

class RDFproperty(Attribute):
	def __init__(self):
		self.uri = uri
		self.label = label
		self.domain = domain #OEM Class?
		self.range = range
'''
import traceback
import uuid
import datetime

# from rdflib import RDF, RDFS, URIRef, Namespace, XSD, Literal
from rdflib import Graph

from vdm.namespaces import D, BCITE

PROV = 'http://www.w3.org/ns/prov#'
BPROV = 'http://vivo.brown.edu/ontology/provenance#'
OWL = 'http://www.w3.org/2002/07/owl#'
RDF = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
RDFS = 'http://www.w3.org/2000/01/rdf-schema#'

class Edge(object):
	def __init__(self):
		pass

# class Node(object):
# 	def __init__(self):
# 		self.values = []

# 	def attach(self, value):
# 		self.values.append(value)

# 	@property
# 	def 

class LODO(object):
	def __init__(self, label=None, uri=None):
		self.ld_instance = {
			"@id": None,
			"@type": list(),
		}
		self.ld_context = {
			"@context": {}
		}
		self.local_context = {
			"label": RDFS + 'label',
		}
		self.rdf_type = OWL + 'Thing'
		self.json_ld = {}
		self.initialize_ld()

	def initialize_ld(self):
		#self.update_ld_context()
		self.ld_context["@context"].update(
			self.local_context
		)
		#self.update_ld_instance()
		self.ld_instance['@type'].append(self.rdf_type)
		for k in self.local_context.keys():
			self.ld_instance[k] = set()
		#self.init_json_ld()
		self.json_ld = self.ld_context.copy()
		self.json_ld.update(self.ld_instance)

class PROVactivity(LODO):
	def __init__(self):
		super(PROVactivity, self).__init__()
		self.rdf_type = PROV + 'Activity'
		self.local_context = {
			'was_associated_with': {
				'@id': PROV + 'wasAssociatedWith',
				'@type': ['@id', PROV + 'Agent']
			},
			'used': {
				'@id': PROV + 'used',
				'@type': ['@id', PROV + 'Entity']
			},
			'generated_statement': {
				'@id': BPROV + 'generatedStatement',
				'@type': ['@id', RDF + 'Statement']
			}
		}
		self.initialize_ld()

	def was_associated_with(self, agent=None):
		if agent is None:
			return self.ld_instance['was_associated_with']
		else:
			self.ld_instance['was_associated_with'].add(agent)

class RDFstatement(LODO):
	def __init__(self):
		super(RDFstatement, self).__init__()
		self.rdf_type = RDF + 'Statement'
		self.local_context = {
			'action': BPROV + 'action',
			'subject': RDF + 'subject',
			'predicate': RDF + 'predicate',
			'object': RDF + 'object',
			'statement_generated_by': BPROV + 'statementGeneratedBy'
		}
		self.initialize_ld()

# def make_timestamp():
# 	dt = datetime.datetime.utcnow()
# 	tstamp = Literal(dt,datatype=XSD.dateTime)
# 	return tstamp

# def make_prov_object(uri, label, prov_class):
# 	label_literal = Literal(label)
# 	prov_type = get_prov_class(prov_class)
# 	g = Graph()
# 	triples = [
# 		(uri, RDF['type'], prov_type),
# 		(uri, RDFS['label'], label_literal),
# 	]
# 	for t in triples:
# 		g.add(t)
# 	return g

# def get_prov_class(class_string):
# 	class_string = class_string.lower()
# 	class_map = {
# 		'activity': PROV['Activity'],
# 		'entity': PROV['Entity'],
# 		'agent': PROV['Agent']
# 	}
# 	try:
# 		obj_type = class_map[class_string]
# 	except KeyError:
# 		raise
# 	return obj_type

# def make_activity_datetime(actv_uri, datetime):
# 	g = Graph()
# 	triples = [
# 		(actv_uri, PROV['startedAtTime'], datetime),
# 		(actv_uri, PROV['endedAtTime'], datetime),
# 	]
# 	for t in triples:
# 		g.add(t)
# 	return g

# def make_statement_rdf(stmt_uri,activity_uri,action,s,p,o):
# 	g = Graph()
# 	triples = [
# 		(stmt_uri, RDF['type'], RDF['Statement']),
# 		(stmt_uri, BPROV['action'], action),
# 		(stmt_uri, BPROV['statmentGeneratedBy'], activity_uri),
# 		(activity_uri, BPROV['generatedStatement'], stmt_uri),
# 		(stmt_uri, RDF['subject'], s),
# 		(stmt_uri, RDF['predicate'], p),
# 		(stmt_uri, RDF['object'], o)
# 	]
# 	for t in triples:
# 		g.add(t)
# 	return g


# class ActivityLogger(object):
# 	def __init__(self):
# 		self.label = 'Activity'
# 		self.logger = logger
# 		self.activity_uri = mint_uuid_uri()
# 		self.entities = []
# 		self.agents = []
# 		self.add_triples = Graph()
# 		self.remove_triples = Graph()
# 		self.graph = Graph()

# 	def add_rdf(self, graph):
# 		self.add_triples += graph

# 	def remove_rdf(self, graph):
# 		self.remove_triples += graph

# 	def add_software_agent(self):
# 		#consider also LogRecord.pathname
# 		#Need custom Handler
# 		stack = traceback.extract_stack(limit=2)[0]
# 		swAgent = 'Func: {2} File: {0} Line: {1}'.format(*stack)
# 		self.agents.append(swAgent)

# 	def graph_activity(self):
# 		activity_rdf = make_prov_object(
# 			self.activity_uri, self.label, 'activity'
# 			)
# 		dt = make_timestamp()
# 		dt_rdf = make_activity_datetime(self.activity_uri, dt)
# 		self.graph += activity_rdf
# 		self.graph += dt_rdf

# 	def graph_agents(self):
# 		for agent in self.agents:
# 			uri = mint_uuid_uri()
# 			agent_rdf = make_prov_object(uri, agent, 'agent')
# 			activity_rdf = (self.activity_uri, PROV['wasAssociatedWith'], uri)
# 			self.graph.add(activity_rdf)
# 			self.graph += agent_rdf

# 	def graph_entities(self):
# 		for entity in self.entities:
# 			uri = mint_uuid_uri()
# 			entity_rdf = make_prov_object(uri, entity, 'entity')
# 			activity_rdf = (self.activity_uri, PROV['used'], uri)
# 			self.graph.add(activity_rdf)
# 			self.graph += entity_rdf

# 	def graph_statements(self):
# 		for s,p,o in self.add_triples.triples((None,None,None)):
# 			stmt = mint_uuid_uri()
# 			action = D['bprov-Add']
# 			stmt_rdf = make_statement_rdf(
# 				stmt,self.activity_uri,action,s,p,o
# 				)
# 			self.graph += stmt_rdf
# 		for s,p,o in self.remove_triples.triples((None,None,None)):
# 			stmt = mint_uuid_uri()
# 			action = D['bprov-Remove']
# 			stmt_rdf = make_statement_rdf(
# 				stmt,self.activity_uri,action,s,p,o
# 				)
# 			self.graph += stmt_rdf

# 	def log(self):
# 		self.graph_activity()
# 		self.graph_agents()
# 		self.graph_entities()
# 		self.graph_statements()
# 		nt = self.graph.serialize(format='nt')
# 		self.logger.warning(nt)

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
# 		self.label = 'VIVO Manger Logger'

# 	def add_faculty_agent(self, shortid):
# 		self.agents.append(shortid)


