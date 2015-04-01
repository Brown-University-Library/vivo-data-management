
import rdflib
from rdflib import RDFS
from rdflib.query import ResultException

from vdm.namespaces import FOAF, VIVO, BLOCAL, TMP


class BaseResource(rdflib.resource.Resource):
    """
    A superclass for local resources.
    Some code borrowed from:
    https://github.com/tetherless-world/kleio/blob/master/kleio/prov.py
    """

    def __init__(self, uri=None, graph=None):
        #if type(uri) != URIRef:
        #    raise Exception("uri must be a RDFLib URIRef")
        super(BaseResource, self).__init__(graph, uri)

    def get_literals(self, prop):
        """
        Return a list of values of the property 'prop' as
        python native literals.
        """
        return [literal.toPython() for literal
                in self.graph.objects(self.identifier, prop)]

    def get_label(self, first_only=True):
        """
        Return RDFS label of resource
        """
        labels = self.get_literals(RDFS.label)
        if first_only is True:
            return labels[0]
        return labels

    def get_related(self, prop):
        """
        Get object property URIs and labels as list
        with {'uri': ..., 'label', ...} pairs.
        """
        out = []
        for obj in self.graph.objects(subject=self.identifier, predicate=prop):
            for label in self.graph.objects(subject=obj, predicate=RDFS.label):
                uri = obj.toPython()
                label = label.toPython()
                d = {'uri': uri, 'label': label}
                if d not in out:
                    out.append(d)
        return out

    def get_all_related(self):
        """
        Get a list of uri label pairs for all related objects.
        """
        rq = """
        SELECT ?o ?label
        WHERE {
            ?s ?p ?o .
            ?o rdfs:label ?label .
        }
        """
        out = []
        for uri, label in self.graph.query(rq):
            out.append({'uri': uri.toPython(), 'label': label.toPython()})
        return out

    def get_first_literal(self, prop):
        """
        Get the first literal for the given property.
        """
        for literal in self.graph.objects(self.identifier, prop):
            return literal.toPython()


class VResource(BaseResource):
    """
    A Vitro Resource representing a selected set of triples identified
    by passing the init_query to the store.

    Additional methods that are common across resources can be added here.
    """

    def __init__(self, uri=None, store=None):
        if store is None:
            raise Exception("store must be an RDFLib Graph")
        graph = self.init_graph(uri, store)
        super(VResource, self).__init__(uri=uri, graph=graph)

    def init_query(self):
        """
        A SPARQL construct query to fetch triples representing the 'Resource'.

        Queries will bind self.identifier to subject.

        """
        return u"""
        CONSTRUCT {
            ?subject rdf:type ?type ;
                rdfs:label ?label .
        }
        WHERE {
            ?subject rdf:type ?type ;
                rdfs:label ?label .
        }
        """

    def init_graph(self, uri, store):
        """
        Execute the init_query and return a graph object containing
        the constructed triple.
        """
        rq = self.init_query()
        result = store.query(
            rq,
            initBindings=dict(subject=uri)
        )
        try:
            return result.graph
        except ResultException:
            return None

    def overview(self):
        return self.get_first_literal(VIVO.overview)

    def full_image(self):
        return self.get_first_literal(TMP.fullImage)

    def thumbnail(self):
        return self.get_first_literal(TMP.image)


class Person(VResource):

    def init_query(self):
        return u"""
        CONSTRUCT {
            ?subject a foaf:Person ;
                rdfs:label ?name ;
                ?related ?other .
            ?other ?p ?o .
        }
        WHERE {
            ?subject a foaf:Person ;
                rdfs:label ?name ;
                ?related ?other .
            ?other ?p ?o .
        }
        """


class FacultyMember(VResource):
    """
    For faculty.
    """

    def init_query(self):
        """
        A SPARQL construct query to pull out triples for a faculty resource.
        """
        rq = """
        CONSTRUCT {
            ?subject a vivo:FacultyMember ;
                #label, first, last, email required
                rdfs:label ?name ;
                foaf:firstName ?first ;
                foaf:lastName ?last ;
                vivo:preferredTitle ?title ;
                tmp:email ?email ;
                vivo:overview ?overview ;
                blocal:hasAffiliation ?org ;
                vivo:hasResearchArea ?ra ;
                tmp:image ?photo ;
                tmp:fullImage ?miURL ;
                blocal:hasGeographicResearchArea ?rag .
            #affils
            ?org rdfs:label ?orgName .
            #research areas
            ?ra rdfs:label ?raName .
            #geo research area
            ?rag rdfs:label ?ragName .
        }
        WHERE {
            #required - label, first, last
            {
            ?subject a vivo:FacultyMember ;
                rdfs:label ?name ;
                foaf:firstName ?first ;
                foaf:lastName ?last .
            }
            #optional - title
            UNION {
                ?subject vivo:preferredTitle ?title .
            }
            #optional - email
            UNION {
                ?subject vivo:primaryEmail ?email .
            }
            #optional - overview
            UNION {
                ?subject vivo:overview ?overview .
            }
            #optional - affiliations
            UNION {
                ?subject blocal:hasAffiliation ?org .
                ?org rdfs:label ?orgName .
            }
            #optional - research areas
            UNION {
                ?subject vivo:hasResearchArea ?ra .
                ?ra a blocal:ResearchArea ;
                    rdfs:label ?raName .
            }
            #optional - research places
            UNION {
                ?subject blocal:hasGeographicResearchArea ?rag .
                ?rag a blocal:Place ;
                    rdfs:label ?ragName .
            }
            #optional - photos
            UNION {
                ?subject vitropublic:mainImage ?mi .
                #main image
                ?mi vitropublic:downloadLocation ?miDl .
                ?miDl vitropublic:directDownloadUrl ?miURL .
                #thumbnail
                ?mi vitropublic:thumbnailImage ?ti .
                ?ti vitropublic:downloadLocation ?dl .
                ?dl vitropublic:directDownloadUrl ?photo .
            }
        }
        """
        return rq

    def first(self):
        return self.get_first_literal(FOAF.firstName)

    def last(self):
        return self.get_first_literal(FOAF.lastName)

    def email(self):
        return self.get_first_literal(TMP.email)

    def middle(self):
        return self.get_first_literal(VIVO.middleName)

    def title(self):
        return self.get_first_literal(VIVO.preferredTitle)

    def membership(self):
        return self.get_related(BLOCAL.hasAffiliation)

    def topics(self):
        return self.get_related(VIVO.hasResearchArea)

    def places(self):
        return self.get_related(BLOCAL.hasGeographicResearchArea)




###########################
###### Copy n' Paste ######
###########################


import datetime
import logging
import random
import uuid

#For handling dates.
from dateutil.parser import parse as date_parser

#RDF utils
from rdflib import (
    ConjunctiveGraph,
    Namespace,
    Graph,
    URIRef,
    Literal
)

from rdfalchemy.rdfSubject import rdfSubject
from rdfalchemy import rdfSingle, rdfMultiple

#Namespaces
from rdflib import RDFS, RDF, OWL, XSD
from rdflib.namespace import NamespaceManager, ClosedNamespace

#setup namespaces
#code inspired by / borrowed from https://github.com/libris/librislod
VIVO = Namespace('http://vivoweb.org/ontology/core#')
VITROPUBLIC = Namespace('http://vitro.mannlib.cornell.edu/ns/vitro/public#')
VITRO = Namespace('http://vitro.mannlib.cornell.edu/ns/vitro/0.7#')
DCTERMS = Namespace('http://purl.org/dc/terms/')
BIBO = Namespace('http://purl.org/ontology/bibo/')
FOAF = Namespace('http://xmlns.com/foaf/0.1/')
SKOS = Namespace('http://www.w3.org/2004/02/skos/core#')
#local ontology
BLOCAL = Namespace('http://vivo.brown.edu/ontology/vivo-brown/')
#local data namespace
D = Namespace('http://vivo.brown.edu/individual/')
#aleas for now.
BU = D
BCITE = Namespace('http://vivo.brown.edu/ontology/citation#')

namespaces = {}
for k, o in vars().items():
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

def uri_from_qname(qstring):
    prefix, classname = qstring.split(':')
    uri = namespaces[prefix.upper()][classname]
    return uri

def init_graph():
    """
    Helper to initialize a VIVO graph with
    namespace manager.
    """
    g = Graph()
    g.namespace_manager = ns_mgr
    return g

def make_uuid_uri(ns, prefix='n'):
    """
    Create a unique url.
    """
    u = str(uuid.uuid1())
    if prefix is not None:
        uri = URIRef("%s%s%s" % (ns, prefix, u))
    else:
        uri = URIRef(ns + u)
    return uri

class FusekiGraph(ConjunctiveGraph):
    """
    Connect to a Fueski VIVO instance.
    """
    def __init__(self, endpoint):
        ConjunctiveGraph.__init__(self, 'SPARQLStore')
        self.open(endpoint)
        self.namespace_manager=ns_mgr


class VStore(FusekiGraph):

    def get_next_uri(self, prefix='n', number=1, used_uris=[], max=99999):
        """
        Mint new URIs in the VIVO pattern (e.g. n1234).
        SPARQL interpretation of getNextURI here:
        http://svn.code.sf.net/p/vivo/vitro/code/branches/dev-sdb/webapp/src/edu/cornell/mannlib/vitro/webapp/utils/jena/JenaIngestUtils.java
        """
        count = 0
        out = []
        minted_uris = 0
        while True:
            next_uri = URIRef(D + prefix + str(random.randint(1, max)))
            #Make sure we haven't used this URI already.
            if next_uri in used_uris:
                continue
            if next_uri in out:
                continue
            count += 1
            q = """
            SELECT ?o ?s2
            WHERE {{
                OPTIONAL{{<{0}> ?p ?o}}.
                OPTIONAL{{?s2 ?p2 <{0}>}}.
            }}
            """.format(next_uri)
            results = [row for row in self.query(q)]
            #Make sure result set is empty.
            if results == [(None, None)]:
                minted_uris += 1
                out.append(next_uri)
                #Don't create more uris than was requested.
                if minted_uris >= number:
                    break
            else:
                #Raise an exception if we try 50 URIs and none are 'new'.
                #This probably means something is wrong.
                logging.debug("{0} is an assigned URI.  Trying again.".format(next_uri))
                if count == 50:
                    raise Exception("""
                        50 random uris were tried and none returned
                        a unique uri.  Verify or increase max random uri.""")
        if number == 1:
            return out[0]
        else:
            return out

class VGraph(Graph):

    def __init__(self):
        Graph.__init__(self, namespace_manager=ns_mgr)

    def construct(self, query, bind={}):
        """
        Returns a new Graph with data returned
        by the construct query.

        Pass in a dictionary bind with values to replace
        in the query
        """
        out = init_graph()
        prepped_query = prep_query(query, bind)
        logging.debug(prepped_query)
        results = self.query(prepped_query)
        if results.graph is None:
            return
        else:
            out += results.graph
            return out

    def select(self, query, bind={}):
        """
        Return RDFLib SPARQL query results for the query.

        Pass in a dictionary bind with values to replace
        in the query.
        """
        prepped_query = prep_query(query, bind)
        logging.debug(prepped_query)
        return self.query(prepped_query)

#
# - use RDFAlchemy to map pubmed.
#

from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore
from rdflib import URIRef, ConjunctiveGraph

DEFAULT_GRAPH = URIRef('http://vivo.brown.edu/data/')

class UpdateStore(ConjunctiveGraph):

    def __init__(self, query_endpoint, update_endpoint, store='SPARQLUpdateStore', identifier=None):
        super(UpdateStore, self).__init__(store, identifier=identifier)
        self.open((
            query_endpoint,
            update_endpoint,
        ))

    def _do(self, q):
        print q
        r = self.store._do_update(q)
        content = r.read()  # we expect no content
        if r.status not in (200, 204):
            raise Exception("Could not update: %d %s\n%s" % (
                r.status, r.reason, content))

    def graph_add(self, graph, name=None):
        """
        See:
        https://github.com/RDFLib/rdflib/blob/master/rdflib/plugins/stores/sparqlstore.py#L451
        """
        nameg = name or DEFAULT_GRAPH
        data = ""
        for subject, predicate, obj in graph:
            triple = u"%s %s %s .\n" % (subject.n3(), predicate.n3(), obj.n3())
            data += triple
        query = u"INSERT DATA \n { GRAPH <%s> {\n %s }\n}" % (nameg, data)
        self._do(query)

    def graph_remove(self, graph, name=None):
        nameg = name or DEFAULT_GRAPH
        data = ""
        for subject, predicate, obj in graph:
            triple = u"%s %s %s .\n" % (subject.n3(), predicate.n3(), obj.n3())
            data += triple
        query = u"DELETE DATA \n { GRAPH <%s> { %s }\n}" % (nameg, data)
        self._do(query)


def make_pub_year(raw):
    dv = date_parser(str(raw))
    #Set to Jan 1
    nv = datetime.date(year=dv.year, month=1, day=1)
    return nv

class Contributor(rdfSubject):
    rdf_type = BCITE.Contributor

class Venue(rdfSubject):
    rdf_type = BCITE.Venue
    label = rdfSingle(RDFS.label)
    issn = rdfSingle(BCITE.issn)
    eissn = rdfSingle(BCITE.eissn)
    isbn = rdfSingle(BCITE.isbn)

    #In production we might want this method to fetch an existing
    #URI for a passed in ISSN.
    def __init__(self, resUri=None, **kwargs):
        """
        Override parent init to construct URI to attempt to create
        a URI based on the issn.
        """
        issn = kwargs.get('issn')
        eissn = kwargs.get('eissn')
        isbn = kwargs.get('isbn')
        if (resUri is None) and ((issn is not None) or (eissn is not None) or (isbn is not None)):
            if issn is not None:
                resUri = URIRef(D + 'jrnl-{}'.format(issn))
            if isbn is not None:
                resUri = URIRef(D + 'book-{}'.format(isbn))
            if eissn is not None:
                resUri = URIRef(D + 'jrnl-{}'.format(eissn))
            self.resUri = resUri
            self.db.add((resUri, RDF.type, BCITE.Venue))
            self._set_with_dict(kwargs)
            return
        super(Venue, self).__init__(resUri=resUri, **kwargs)

class Citation(rdfSubject):
    rdf_type = BCITE.Citation
    label = rdfSingle(RDFS.label)
    title = rdfSingle(BCITE.title)
    doi = rdfSingle(BCITE.doi)
    pmid = rdfSingle(BCITE.pmid)
    pmcid = rdfSingle(BCITE.pmcid)
    volume = rdfSingle(BCITE.volume)
    issue = rdfSingle(BCITE.issue)
    pages = rdfSingle(BCITE.pages)
    date = rdfSingle(BCITE.date)
    #author list
    authorList = rdfSingle(BCITE.authorList)
    #venue
    hasVenue = rdfSingle(BCITE.hasVenue, range_type=BCITE.Venue)
    #contributor
    hasContributor = rdfMultiple(BCITE.hasContributor, range_type=BCITE.Contributor)

class Article(Citation):
    rdf_type = BCITE.Article

class Chapter(Citation):
    rdf_type = BCITE.Chapter