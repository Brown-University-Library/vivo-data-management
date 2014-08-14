# -*- coding: utf-8 -*-
from pprint import pprint
import os

from rdflib import URIRef, RDF, RDFS, OWL

from .tutils import load, BTest
from dateutil import parser
import datetime

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

        date = prepped['date']
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

        date = g.value(subject=pub_uri, predicate=BCITE.date)
        dtv = date.toPython()
        #Make sure our dates are datetime.date and not datetime.datetime.
        assert(type(dtv) == datetime.date)
        assert(dtv.year == 2013)
        assert(dtv.month == 12)

    def test_rdf_venue_uri(self):
        venue_uri = D['v123']
        article = Publication()
        meta = article.prep(self.meta, venue_uri=venue_uri)
        g = article.to_graph(meta)
        g.namespace_manager = ns_mgr
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

class TestArticleUnicode(BTest):
    """
    Test an article with umlaut to make sure unicode is
    occuring properly.
    """
    def setUp(self):
        self.pmid = '24948623'
        raw_data = load('pubmed_article_unicode.json')
        self.meta = raw_data['result'][self.pmid]

    def test_meta(self):
        article = Publication()
        prepped = article.prep(self.meta)
        self.eq(
            u'Survival trends in Waldenström macroglobulinemia: an analysis of the Surveillance, Epidemiology and End Results database.',
            prepped['title']
        )
        self.eq(
            u'Blood',
            prepped['venue']['label']
        )
        self.eq(u'123', prepped['volume'])

        dtv = prepped['date']
        self.eq(2014, dtv.year)
        self.eq(6, dtv.month)
        assert(type(dtv) == datetime.date)

    def test_rdf(self):
        pub_uri = D['n123']
        article = Publication()
        meta = article.prep(self.meta, pub_uri=pub_uri)
        g = article.to_graph(meta)
        g.namespace_manager = ns_mgr
        #ids
        pmid = g.value(subject=pub_uri, predicate=BCITE.pmid)
        self.eq(self.pmid, pmid.toPython())
        doi = g.value(subject=pub_uri, predicate=BCITE.doi)
        self.eq(u'10.1182/blood-2014-05-574871', doi.toPython())

        title = g.value(subject=pub_uri, predicate=RDFS.label)
        assert(
            title.toPython().startswith(u'Survival trends in Waldenström macroglobulinemia:')
        )


class TestBook(BTest):
    """
    This article's title was failing.
    """
    def setUp(self):
        self.pmid = '22553887'
        raw_data = load('pubmed_book.json')
        self.meta = raw_data['result'][self.pmid]

    def test_meta(self):
        article = Publication()
        prepped = article.prep(self.meta)
        self.eq(
            u'Comprehensive Overview of Methods and Reporting of Meta-Analyses of Test Accuracy',
            prepped['title']
        )
        date = prepped['date']
        self.eq(2012, date.year)

        authors = prepped['authors']
        assert(
            u"Schmid" in authors
        )

        assert(
            prepped['url'] == u"http://www.ncbi.nlm.nih.gov/books/NBK92422/"
        )

    def test_rdf(self):
        pub_uri = D['n123']
        book = Publication()
        meta = book.prep(self.meta, pub_uri=pub_uri)
        g = book.to_graph(meta)
        g.namespace_manager = ns_mgr
        #ids
        pmid = g.value(subject=pub_uri, predicate=BCITE.pmid)
        self.eq(self.pmid, pmid.toPython())
        #No venue
        venue = g.value(subject=pub_uri, predicate=BCITE.hasVenue)
        assert(venue == None)
        ctype = g.value(subject=pub_uri, predicate=RDF.type)
        self.eq(ctype, BCITE.Book)

        title = g.value(subject=pub_uri, predicate=RDFS.label)
        assert(
            title.toPython().startswith(u'Comprehensive Overview of Methods and Reporting of Meta-Analyses of Test Accuracy')
        )

        url = g.value(subject=pub_uri, predicate=BCITE.url)
        assert(
            url.toPython() == u"http://www.ncbi.nlm.nih.gov/books/NBK92422/"
        )

class TestChapter(BTest):

    def setUp(self):
        self.pmid = '21413284'
        raw_data = load('pubmed_chapter.json')
        self.meta = raw_data['result'][self.pmid]

    def test_meta(self):
        article = Publication()
        prepped = article.prep(self.meta)
        self.eq(
            u'Epidemiology',
            prepped['title']
        )
        date = prepped['date']
        self.eq(1996, date.year)

        authors = prepped['authors']
        assert(
            u"Brachman" in authors
        )

        self.eq(
            u'Medical Microbiology',
            prepped['book']
        )

    def test_rdf(self):
        pub_uri = D['n123']
        book = Publication()
        meta = book.prep(self.meta, pub_uri=pub_uri)
        g = book.to_graph(meta)
        g.namespace_manager = ns_mgr
        #ids
        pmid = g.value(subject=pub_uri, predicate=BCITE.pmid)
        self.eq(self.pmid, pmid.toPython())
        #No venue
        venue = g.value(subject=pub_uri, predicate=BCITE.hasVenue)
        assert(venue == None)
        ctype = g.value(subject=pub_uri, predicate=RDF.type)
        self.eq(ctype, BCITE.BookSection)

        title = g.value(subject=pub_uri, predicate=RDFS.label)
        assert(
            title.toPython().startswith(u'Epidemiology')
        )

        book = g.value(subject=pub_uri, predicate=BCITE.book)
        assert(
            book.toPython().startswith(u'Medical Microbiology')
        )

def test_id_convert():
    """
    Test the idconvert tool.

    API response format varies from a non-matching
    recognized identifier to a non-matching unrecognized
    identifier.
    """
    from vdm.pubmed import id_convert

    #Should return match
    meta = id_convert('10.1371/journal.pmed.0040305')
    assert(
        meta['pmid'] == '18001145'
    )

    #DOI identified but should not match
    meta = id_convert('10.2514/1.J051183baddoi')
    assert (
        meta is None
    )

    #Uknown identifier type - should not match
    meta = id_convert('badIDSentToServiceForTesting')
    assert (
        meta is None
    )


def test_doi_search():
    from vdm.pubmed import doi_search
    doi = u"10.1097/dbp.0000000000000060"
    rsp = doi_search(doi)
    assert(
        rsp == "24906035"
    )