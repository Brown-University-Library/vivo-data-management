
from rdflib import Literal, RDF, RDFS
from vdm.namespaces import D, FOAF

from vdm.backend import work_graph
from vdm.models import VResource, Person, FacultyMember


class TestResource:
    def setup_class(self):
        uri = D["jsmith"]
        name = Literal(u"Smith, Joe")
        g = work_graph()
        g += [
            (uri, RDF.type, FOAF.Person),
            (uri, RDFS.label, name)
        ]
        self.graph = g
        self.name = name
        self.uri = uri

    def test_base_resource(self):
        res = VResource(uri=self.uri, store=self.graph)
        assert res.get_label() == self.name.toPython()
        assert res.graph.value(subject=self.uri, predicate=RDF.type)\
            == FOAF.Person
        assert (res.get_first_literal(RDFS.label) == self.name.toPython())

    def test_person(self):
        other = D['bob']
        name = Literal("Jones, Bob")
        self.graph += [
            (self.uri, FOAF.knows, other),
            (other, RDFS.label, name)
        ]
        res = Person(uri=self.uri, store=self.graph)
        assert res.get_label() == self.name.toPython()
        assert res.graph.value(subject=self.uri, predicate=RDF.type)\
            == FOAF.Person
        related = res.get_related(FOAF.knows)
        assert other.toPython() in [r['uri'] for r in related]
        assert name.toPython() in [r['label'] for r in related]


class TestFaculty:
    def setup_class(self):
        test_data = u"""
        @prefix blocal: <http://vivo.brown.edu/ontology/vivo-brown/> .
        @prefix foaf:  <http://xmlns.com/foaf/0.1/> .
        @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        @prefix vivo:  <http://vivoweb.org/ontology/core#> .
        @prefix d: <http://vivo.brown.edu/individual/>.

        d:jcarberry a vivo:FacultyMember;
            rdfs:label "Carberry, Josiah" ;
            foaf:firstName "Josiah" ;
            foaf:lastName "Carberry" ;
            vivo:primaryEmail "jcarberry@brown.edu" ;
            blocal:hasAffiliation d:org1 ;
            vivo:preferredTitle "Prof of History" ;
            vivo:hasResearchArea d:topic1 ;
            vivo:overview "Researcher" .

        #Fac with minimal attributes.
        d:jsmith a vivo:FacultyMember ;
            rdfs:label "Smith, John" ;
            foaf:firstName "John" ;
            foaf:lastName "Smith" .

        d:topic1 a blocal:ResearchArea ;
            rdfs:label "Medicine" ;
            vivo:researchAreaOf d:jcarberry .

        d:org1 a foaf:Organization ;
            rdfs:label "History" .
        """
        test_store = work_graph()
        test_store.parse(data=test_data, format='turtle')
        self.store = test_store

    def test_faculty(self):
        """Test faculty attributes"""
        fac = FacultyMember(uri=D["jcarberry"], store=self.store)
        assert fac.get_label() == u"Carberry, Josiah"
        assert fac.first() == u"Josiah"
        assert fac.last() == u"Carberry"
        assert fac.middle() is None
        assert fac.email() == "jcarberry@brown.edu"
        assert fac.title() == u"Prof of History"
        membership = fac.membership()
        assert {'uri': u'http://vivo.brown.edu/individual/org1', 'label': u'History'}\
            in membership
        assert fac.overview() == u"Researcher"
