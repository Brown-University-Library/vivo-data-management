import logging
logger = logging.getLogger(__name__)

from rdflib import (
    Graph,
    ConjunctiveGraph,
    Literal,
    RDF,
    RDFS,
    URIRef
)
from rdflib.query import ResultException
from SPARQLWrapper import SPARQLWrapper

import uuid

from .utils import get_env

from .namespaces import (
    namespaces,  #dict of namespaces
    ns_mgr,
    D,  #data namespace
)


class BaseBackend:
    """
    Common methods for all backends.
    """

    def uuid_uri(self, prefix='n'):
        return D[str(prefix) + str(uuid.uuid4())]

    def local_name(self, uri):
        """
        Strip out the data namespace for local names.
        """
        raw = uri.toPython()
        if D not in raw:
            raise VIVODataError('URI not local namespace - {0}'.format(raw))
        return raw.replace(D, '')

    def get_prop_from_abbrv(self, prefix_prop):
        prefix, prop = prefix_prop.split(':')
        ns = namespaces.get(prefix.upper())
        if ns is None:
            raise Exception("Unknown namespace prefix: {}.".format(prefix))
        return ns[prop]

    def create_resource(self, vtype, text, uri=None):
        if uri is None:
            uri = self.uuid_uri()
        vclass = self.get_prop_from_abbrv(vtype)
        g = Graph()
        g.add((uri, RDFS.label, Literal(text)))
        g.add((uri, RDF.type, vclass))
        return (uri, g)

    def make_edit_graph(self, triple):
        g = Graph()
        if triple == {}:
            return g
        prefix, prop = triple['predicate'].split(':')
        ns = namespaces.get(prefix.upper())
        if ns is None:
            raise Exception("Unknown namespace prefix: {}.".format(prefix))
        pred = URIRef(ns[prop])
        obj = triple.get('object')
        subj = URIRef(triple['subject'])
        is_uri = False
        try:
            is_uri = str(obj).startswith('http')
        except Exception as e:
            logger.warning("Encoding error editing object.")
            logger.warning(e)
        if is_uri is True:
            obj = URIRef(obj)
        else:
            obj = Literal(obj)
        g.add((
            subj,
            pred,
            obj,
        ))
        return g

    def get_subtract_graph(self, triple):
        """
        This is assuming that a functional property is being edited.
        """
        if triple == {}:
            return Graph()
        #We will leave the object blank.
        q = """
        CONSTRUCT {{
            <{0}> {1} ?object
        }}
        WHERE {{
            <{0}> {1} ?object
        }}
        """.format(triple['subject'], triple['predicate'])
        try:
            results = self.graph.query(q)
            subtract_graph = results.graph
        except ResultException:
            return Graph()
        return subtract_graph

    def add_remove(self, *args):
        raise NotImplementedError("Add and remove not defined.")


class VIVOBackend(BaseBackend):
    """
    Interface for adding data to a VIVO 1.6+ SPARQL Update backend.
    """

    def __init__(self, endpoint):
        graph = ConjunctiveGraph('SPARQLStore')
        graph.open(endpoint)
        graph.namespace_manager = ns_mgr
        self.graph = graph
        self.default_graph = \
            'http://vitro.mannlib.cornell.edu/default/vitro-kb-2'

    def do_update(self, query):
        logger.debug(query)
        update_url = get_env('VIVO_URL') + '/api/sparqlUpdate'
        sparql = SPARQLWrapper(update_url)
        sparql.addParameter('email', get_env('VIVO_USER'))
        sparql.addParameter('password', get_env('VIVO_PASSWORD'))
        sparql.method = 'POST'
        sparql.setQuery(query)
        results = sparql.query()
        return results

    def build_clause(self, change_graph, name=None, delete=False):
        nameg = name or self.default_graph
        stmts = ''
        for subject, predicate, obj in change_graph:
            triple = "%s %s %s .\n" % (subject.n3(), predicate.n3(), obj.n3())
            stmts += triple
        if delete is False:
            return u"INSERT DATA { GRAPH <%s> { %s } }" % (nameg, stmts)
        else:
            return u"DELETE DATA { GRAPH <%s> { %s } }" % (nameg, stmts)

    def add_remove(self, add_g, subtract_g, name=None):
        """
        #DELETE { GRAPH <g1> { a b c } } INSERT { GRAPH <g1> { x y z } }
        #http://www.w3.org/TR/sparql11-update/#deleteInsert
        #return self.primitive_edit(add_g, subtract_g)
        """
        rq = ''
        add_size = len(add_g)
        remove_size = len(subtract_g)
        if (add_size == 0) and (remove_size == 0):
            logging.info("Graphs empty.  No edit made.")
        if add_size != 0:
            rq += self.build_clause(add_g, name=name)
        if remove_size != 0:
            rq += ' ' + self.build_clause(subtract_g, name=name, delete=True)
        logger.debug("SPARQL Update Query:\n".format(rq))
        self.do_update(rq)
        return True


class FusekiGraph(ConjunctiveGraph):
    """
    Connect to a Fueski VIVO instance.
    """
    def __init__(self, endpoint):
        ConjunctiveGraph.__init__(self, 'SPARQLStore')
        self.open(endpoint)
        self.namespace_manager = ns_mgr


def work_graph():
    """
    Get an in memory graph with the default
    namespace_manager set.
    """
    g = Graph()
    g.namespace_manager = ns_mgr
    return g


class VIVOEditError(Exception):
    def __init__self(self, message, Errors):
        #http://stackoverflow.com/questions/1319615/proper-way-to-declare-custom-exceptions-in-modern-python
        Exception.__init__(self, message)
        self.Errors = Errors


class VIVODataError(Exception):
    def __init__self(self, message, Errors):
        #http://stackoverflow.com/questions/1319615/proper-way-to-declare-custom-exceptions-in-modern-python
        Exception.__init__(self, message)
        self.Errors = Errors
