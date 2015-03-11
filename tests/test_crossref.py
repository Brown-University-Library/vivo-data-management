from pprint import pprint
import json

import pytest
from rdflib import URIRef, RDFS

from .tutils import load, BTest

from vdm.utils import get_env

from vdm.crossref import Publication
from vdm.namespaces import ns_mgr, BCITE, D, DCTERMS

import datetime

import vcr

try:
    get_env('TRAVIS')
    TRAVIS = True
except Exception:
    TRAVIS = False

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
        uri = D['n123']
        meta['uri'] = uri
        g = article.to_graph(meta)
        g.namespace_manager = ns_mgr
        #check venue
        rq = """
        select ?issn ?vtype
        where {
            ?p bcite:hasVenue ?venue .
            ?venue bcite:issn ?issn .
            ?venue a ?vtype .
        }
        """
        results = [r for r in g.query(rq)]
        if results == []:
            raise Exception("Query returned no results.")
        for row in results:
            self.eq(u'0022-3476', row.issn.toPython())
            self.eq(row.vtype, BCITE.Venue)

        date_literal = g.value(subject=uri, predicate=BCITE.date)
        date_value = date_literal.toPython()
        assert(date_value == datetime.date(2013, 12, 1))
        #Make sure our dates are datetime.date and not datetime.datetime.
        assert(type(date_value) == datetime.date)
        assert(date_value.year == 2013)
        assert(date_value.month == 12)


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
        assert(prepped['date'] == datetime.date(1900, 1, 1))

    def test_rdf(self):
        #give book a URI
        uri = D['n123']
        pub = Publication()
        prepped = pub.prep(self.meta)
        prepped['uri'] = uri
        g = pub.to_graph(prepped)
        g.namespace_manager = ns_mgr
        date_literal = g.value(subject=uri, predicate=BCITE.date)
        date_value = date_literal.toPython()
        assert(date_value == datetime.date(1900, 1, 1))
        #Make sure our dates are datetime.date and not datetime.datetime.
        assert(type(date_value) == datetime.date)
        assert(date_value.year == 1900)
        assert(date_value.month == 1)

        title = g.value(subject=uri, predicate=RDFS.label)
        assert(title.toPython() == u"Pagan Virtue")

        doi = g.value(subject=uri, predicate=BCITE.doi)
        assert(doi.toPython() == self.doi)

class TestConferencePaper(BTest):

    def setUp(self):
        self.doi = '10.1145/1531542.1531578'
        raw = load('crossref_conf-paper.json')
        self.meta = raw

    def test_meta(self):
        pub = Publication()
        prepped = pub.prep(self.meta)
        assert(prepped['title'] == u"Energy-optimal synchronization primitives for single-chip multi-processors")
        assert(prepped['doi'] == self.doi)
        assert(prepped['date'] == datetime.date(2009, 1, 1))
        assert(prepped['published_in'] == u"Proceedings of the 19th ACM Great Lakes symposium on VLSI - GLSVLSI '09")

    def test_rdf(self):
        #give book a URI
        uri = D['n123']
        pub = Publication()
        prepped = pub.prep(self.meta)
        prepped['uri'] = uri
        g = pub.to_graph(prepped)
        g.namespace_manager = ns_mgr
        date_value = g.value(subject=uri, predicate=BCITE.date)
        assert(date_value.toPython() == datetime.date(2009, 1, 1))

        title = g.value(subject=uri, predicate=RDFS.label)
        assert(title.toPython() == u"Energy-optimal synchronization primitives for single-chip multi-processors")

        doi = g.value(subject=uri, predicate=BCITE.doi)
        assert(doi.toPython() == self.doi)

        container = g.value(subject=uri, predicate=BCITE.publishedIn)
        assert(container.toPython() ==u"Proceedings of the 19th ACM Great Lakes symposium on VLSI - GLSVLSI '09")
        #assert(self.eq(1, 2))

@pytest.mark.skipif(TRAVIS is True, reason="run locally")
def test_fetch():
    import os
    from vdm.crossref import get_citeproc, get_crossref_rdf
    os.environ['VDM_USER_AGENT'] = 'Test client https://github.com/Brown-University-Library/vivo-data-management'
    doi = '10.1016/j.jpeds.2013.06.032'
    cp = get_citeproc(doi)
    assert(cp.get('container-title') == u'The Journal of Pediatrics')
    assert(cp.get('issue') == u'6')

    #Test RDF fetch
    cr_rdf = get_crossref_rdf(doi)
    uri = 'http://dx.doi.org/' + doi
    title = cr_rdf.value(subject=URIRef(uri), predicate=DCTERMS.title)
    assert(title.toPython().startswith(u'Preterm Infant Linear Growth and Adiposity Gain'))

    del os.environ['VDM_USER_AGENT']
    #Test RDF fetch again
    cr_rdf = get_crossref_rdf(doi)
    uri = 'http://dx.doi.org/' + doi
    title = cr_rdf.value(subject=URIRef(uri), predicate=DCTERMS.title)
    assert(title.toPython().startswith(u'Preterm Infant Linear Growth and Adiposity Gain'))

@vcr.use_cassette('tests/data/vcr/crossref/metadata_search.yaml')
def test_metadata_search():
    from vdm.crossref import metadata_search
    meta = metadata_search('10.1001/jama.2011.563')
    citation = meta[0]['fullCitation']
    assert(citation.find(u'Hospitalist Efforts and Improving Discharge') > -1)
    doi = meta[0]['doi']
    assert(doi == u'http://dx.doi.org/10.1001/jama.2011.563')

@vcr.use_cassette('tests/data/vcr/crossref/openurl.yaml')
def test_by_openurl():
    from vdm.crossref import by_openurl
    p = {
        'issn': '1431-0651',
        'spage': '221',
        'volume': '19',
        'date': '2015'
    }
    #with vcr.use_cassette('test/data/vcr/crossref_openurl.yaml', filter_query_parameters=['pid']):
    title, doi = by_openurl(p, 'noreply@example.org')
    assert doi == '10.1007/s00792-014-0663-8'
    assert title.startswith('Transposon mutagenesis')
