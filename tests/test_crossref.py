from pprint import pprint
import json

from rdflib import URIRef, RDFS

from .tutils import load, BTest

from vdm.crossref import Publication
from vdm.namespaces import ns_mgr, BCITE, D

from datetime import date

class TestArticle(BTest):

    def setUp(self):
        self.doi = '10.1016/j.jpeds.2013.06.032'
        raw = load('crossref_article.json')
        self.meta = raw

    def test_meta(self):
        pub = Publication()
        prepped = pub.prep(self.meta)
        #print pub.to_graph(prepped).serialize(format='n3')
        prepped['title'] = u'Preterm Infant Linear Growth and Adiposity Gain: Trade-Offs for Later Weight Status and Intelligence Quotient'
        prepped['volume'] = u'163'
        prepped['issue'] = u'6'
        prepped['pages'] = u'1564-1569.e2'

    def test_rdf(self):
        article = Publication()
        meta = article.prep(self.meta)
        g = article.to_graph(meta)
        g.namespace_manager = ns_mgr
        #check venue
        rq = """
        select ?issn
        where {
            ?p bcite:hasVenue ?venue .
            ?venue bcite:issn ?issn .
        }
        """
        results = [r for r in g.query(rq)]
        if results == []:
            raise Exception("Query returned no results.")
        for row in results:
            self.eq(u'0022-3476', row.issn.toPython())

    def test_contrib(self):
        b = {}
        uri = D['n123']
        b['DOI'] = '10.1234'
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

class TestBook(BTest):

    def setUp(self):
        self.doi = '10.1093/acprof:oso/9780198240037.001.0001'
        raw = load('crossref_book.json')
        self.meta = raw

    def test_meta(self):
        pub = Publication()
        prepped = pub.prep(self.meta)
        assert(prepped['title'] == u"Pagan Virtue")
        assert(prepped['doi'] == self.doi)
        assert(prepped['date'] == date(1900, 1, 1))

    def test_rdf(self):
        #give book a URI
        uri = D['n123']
        pub = Publication()
        prepped = pub.prep(self.meta)
        prepped['uri'] = uri
        g = pub.to_graph(prepped)
        g.namespace_manager = ns_mgr
        date_value = g.value(subject=uri, predicate=BCITE.date)
        assert(date_value.toPython() == date(1900, 1, 1))

        title = g.value(subject=uri, predicate=RDFS.label)
        assert(title.toPython() == u"Pagan Virtue")

        doi = g.value(subject=uri, predicate=BCITE.doi)
        assert(doi.toPython() == self.doi)
        #self.eq(1, 2)


