from .utils import get_env


#Namespaces
from rdflib import Graph, Namespace
from rdflib.namespace import NamespaceManager, ClosedNamespace
from rdflib import RDFS, OWL, RDF

#setup namespaces
#code inspired by / borrowed from https://github.com/libris/librislod
#local data namespace
D = Namespace(get_env('DATA_NAMESPACE'))

VIVO = Namespace('http://vivoweb.org/ontology/core#')
VITROPUBLIC = Namespace('http://vitro.mannlib.cornell.edu/ns/vitro/public#')
VITRO = Namespace('http://vitro.mannlib.cornell.edu/ns/vitro/0.7#')
DCTERMS = Namespace('http://purl.org/dc/terms/')
BIBO = Namespace('http://purl.org/ontology/bibo/')
FOAF = Namespace('http://xmlns.com/foaf/0.1/')
SKOS = Namespace('http://www.w3.org/2004/02/skos/core#')

#ARQ functions
AFN = Namespace('http://jena.hpl.hp.com/ARQ/function#')

#local ontologies
BLOCAL = Namespace('http://vivo.brown.edu/ontology/vivo-brown/')
BCITE = Namespace('http://vivo.brown.edu/ontology/citation#')
BPROFILE = Namespace('http://vivo.brown.edu/ontology/profile#')
BDISPLAY = Namespace('http://vivo.brown.edu/ontology/display#')
BWDAY = Namespace('http://vivo.brown.edu/ontology/workday#')

#tmp graph for in memory graphs
TMP = Namespace('http://localhost/tmp#')

namespaces = {}
vars_copy = vars().copy()
for k, o in vars_copy.items():
    if isinstance(o, (Namespace, ClosedNamespace)):
        namespaces[k] = o

ns_mgr = NamespaceManager(Graph())
for k, v in namespaces.items():
    ns_mgr.bind(k.lower(), v)

rq_prefixes = u"\n".join("prefix %s: <%s>" % (k.lower(), v)
                         for k, v in namespaces.items())

prefixes = u"\n    ".join("%s: %s" % (k.lower(), v)
                          for k, v in namespaces.items()
                          if k not in u'RDF RDFS OWL XSD')
#namespace setup complete
