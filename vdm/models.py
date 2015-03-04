
import rdflib

from rdflib import (
    Literal,
    BNode,
    Namespace,
    URIRef,
    Graph,
    RDF,
    RDFS,
)

from rdflib.query import ResultException

from vdm.namespaces import FOAF, VIVO, BLOCAL, SCHEMA


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
                schema:email ?email ;
                vivo:overview ?overview ;
                schema:memberOf ?org ;
                vivo:hasResearchArea ?ra ;
                schema:image ?photo ;
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
        return self.get_first_literal(SCHEMA.email)

    def middle(self):
        return self.get_first_literal(VIVO.middleName)

    def title(self):
        return self.get_first_literal(VIVO.preferredTitle)

    def membership(self):
        return self.get_related(SCHEMA.memberOf)

    def topics(self):
        return self.get_related(VIVO.hasResearchArea)

    def places(self):
        return self.get_related(BLOCAL.hasGeographicResearchArea)
