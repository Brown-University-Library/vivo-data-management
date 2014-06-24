import logging
logger = logging.getLogger(__name__)

from datetime import date

import requests

from rdflib import Graph

from rdflib_jsonld.parser import to_rdf

import context

def pull(meta, k):
    f = lambda x: None if x is u'' else x
    return f(meta.get(k))

def get_crossref_rdf(doi):
    #Use an HTTP cache.
    h = {'Accept': 'application/rdf+xml'}
    handle = requests.get(doi, headers=h)
    try:
        graph = Graph().parse(data=handle.text)
    except Exception, e:
        logger.info("Bad DOI:" + doi + "\n" + e)
        return
    return graph

def get_citeproc(doi):
    #Use an HTTP cache.
    pre = 'http://dx.doi.org/'
    if doi.startswith(pre):
        pass
    else:
        doi = pre + doi
    h = {'Accept': 'application/citeproc+json'}
    handle = requests.get(doi, headers=h)
    try:
        return handle.json()
    except Exception, e:
        logging.error("Bad DOI {0}".format(doi))
        logging.error(e)
        return

class Publication(object):
    def __init__(self, doi):
        self.doi = doi

    def meta(self):
        raw = get_citeproc()
        return raw

    def _author_list(self, meta):
        authors = []
        for au in meta['author']:
            astring = u"{0}, {1}".format(au.get('family'), au.get('given'))
            authors.append(astring)
        if authors == []:
            return None
        else:
            return u", ".join(authors)

    def _pub_date(self, meta):
        dval = meta.get('issued', {})
        dparts = dval['date-parts'][0]
        year = int(dparts[0])
        try:
            month = int(dparts[1])
        except IndexError:
            month = 1
        return date(year=year, month=month, day=1)

    def pub_types(self, meta):
        d = {}
        ptype = pull(meta, 'type')
        if ptype == u'journal-article':
            d['a'] = 'bcite:Article'
        else:
            d['a'] = 'bcite:Citation'
        return d


    def prep(self, meta, pub_uri=None, venue_uri=None):
        bib = {}
        bib['doi'] = pull(meta, 'DOI')

        #pub type
        ptype = self.pub_types(meta)
        bib.update(ptype)

        #one to one mappings
        for k in ['title', 'volume', 'issue']:
            bib[k] = pull(meta, k)

        bib['pages'] = pull(meta, 'page')

        #author list
        bib['authors'] = self._author_list(meta)

        #date
        date = self._pub_date(meta)
        try:
            bib['date'] = date
        except Exception, e:
            logging.warn("Can't create date for {0}.".format(self.doi))
            logging.warn(e)

        #venue
        venue = {}
        if venue_uri is not None:
            venue['uri'] = venue_uri
        venue['label'] = pull(meta, 'container-title')
        venue['issn'] = pull(meta, 'ISSN')
        bib['venue'] = venue

        c = {}
        c.update(context.base)
        c.update(context.publication)
        bib['@context'] = c
        return bib

    def to_graph(self, prepped):
        g = to_rdf(prepped, Graph())
        return g


