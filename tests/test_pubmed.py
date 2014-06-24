
from pprint import pprint
import os

from rdflib import URIRef

from .tutils import load, BTest
from dateutil import parser

from vdm.pubmed import Publication
from vdm.namespaces import ns_mgr, BCITE, D

class TestArticle(BTest):
    def setUp(self):
        self.pmid = '23910982'
        raw_data = load('pubmed_article.json')
        self.meta = raw_data['result'][self.pmid]

    def test_meta(self):
        article = Publication()
        prepped = article.prep(self.meta)
        self.eq(
            u'Preterm infant linear growth and adiposity gain: trade-offs for later weight status and intelligence quotient.',
            prepped['title']
        )
        self.eq(
            u'The Journal of pediatrics',
            prepped['venue']['label']
        )
        self.eq(u'163', prepped['volume'])

        date = parser.parse(prepped['date'])
        self.eq(2013, date.year)
        self.eq(12, date.month)

    def test_rdf(self):
        pub_uri = D['n123']
        article = Publication()
        meta = article.prep(self.meta, pub_uri=pub_uri)
        g = article.to_graph(meta)
        g.namespace_manager = ns_mgr
        #ids
        pmid = g.value(subject=pub_uri, predicate=BCITE.pmid)
        self.eq(u'23910982', pmid.toPython())
        doi = g.value(subject=pub_uri, predicate=BCITE.doi)
        self.eq(u'10.1016/j.jpeds.2013.06.032', doi.toPython())

        #check venue
        rq = """
        select ?issn
        where {
            ?p bcite:hasVenue ?venue .
            ?venue bcite:issn ?issn .
        }
        """
        for row in g.query(rq):
            self.eq(u'0022-3476', row.issn.toPython())

    def test_rdf_venue_uri(self):
        venue_uri = D['v123']
        article = Publication()
        meta = article.prep(self.meta, venue_uri=venue_uri)
        g = article.to_graph(meta)
        g.namespace_manager = ns_mgr
        print g.serialize(format='n3')
        #check venue
        rq = """
        select ?venue
        where {
            ?p bcite:hasVenue ?v .
            ?v rdfs:label ?venue .
        }
        """
        for row in g.query(rq):
            self.eq(u'The Journal of pediatrics', row.venue.toPython())

    def test_contrib(self):
        b = {}
        uri = D['n123']
        b['articleids'] = [{'idtype': 'pubmed', 'value': 'pm1234'}]
        b['title'] = 'Sample article'

        #Try coauthors created as just strings with @baseuris and
        #as RDFLib URI objects.
        ca1 = [
            'jsmith',
            'jjones'
        ]
        ca2 = [
            D['jsmith'],
            D['jjones']
        ]
        for coauthors in [ca1, ca2]:
            pub = Publication()
            prepped = pub.prep(b, pub_uri=uri, contributors=coauthors)
            assert(coauthors[0] in prepped['contributor'])
            assert(coauthors[1] in prepped['contributor'])

            g = pub.to_graph(prepped)
            #Test that all coathors are in the outputted RDF..
            for ob in g.objects(subject=D['n123'], predicate=BCITE.hasContributor):
                ca2.index(ob) > -1
                assert(type(ob) == URIRef)