import logging
logger = logging.getLogger(__name__)

from datetime import date

import requests

from rdflib import Graph

from rdflib_jsonld.parser import to_rdf

import context

from utils import pull, get_user_agent

doi_prefix = 'http://dx.doi.org/'


def get_crossref_rdf(doi):
    if doi.startswith(doi_prefix):
        pass
    else:
        doi = doi_prefix + doi
    h = {'Accept': 'application/rdf+xml'}
    ua = get_user_agent()
    h.update(ua)
    handle = requests.get(doi, headers=h)
    print handle.request.headers
    try:
        graph = Graph().parse(data=handle.text)
    except Exception, e:
        logger.info("Bad DOI:" + doi + "\n" + e)
        return
    return graph

def get_citeproc(doi):
    """
    Get citeproc from CrossRef.
    """
    if doi.startswith(doi_prefix):
        pass
    else:
        doi = doi_prefix + doi
    h = {'Accept': 'application/citeproc+json'}
    ua = get_user_agent()
    h.update(ua)
    handle = requests.get(doi, headers=h)
    try:
        return handle.json()
    except Exception, e:
        logger.error("Bad DOI {0}".format(doi))
        logger.error(e)
        return


class CrossRefSearchException(Exception):
    pass


def metadata_search(search_string):
    """
    Search the metadata API.
    """
    base = "http://search.crossref.org/dois?q={0}".format(search_string)
    resp = requests.get(base, headers=user_agent)
    data = resp.json()
    if len(data) == 0:
        raise CrossRefSearchException("No CR metadata search results")
    else:
        return data


class Publication(object):
    def __init__(self):
        pass

    def fetch(self, doi):
        raw = get_citeproc(doi)
        return raw

    def _author_list(self, meta):
        authors = []
        for au in meta.get('author', []):
            astring = u"{0}, {1}".format(au.get('family'), au.get('given'))
            authors.append(astring)
        if authors == []:
            return None
        else:
            return u", ".join(authors)

    def _pub_date(self, meta):
        dval = meta.get('issued', {})
        dparts = dval.get('date-parts')
        if dparts is None:
            return
        else:
            dgrp = dparts[0]
        try:
            year = int(dgrp[0])
        except Exception:
            #Some DOIs don't have dates issued.
            #Set to 1900 so that we can track these down later.
            return date(year=1900, month=1, day=1)
        try:
            month = int(dgrp[1])
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

    def prep(self, meta, pub_uri=None, venue_uri=None, contributors=[]):
        bib = {}
        doi = pull(meta, 'DOI')
        bib['doi'] = doi

        if pub_uri is not None:
            bib['uri'] = pub_uri

        #pub type
        ptype = self.pub_types(meta)
        bib.update(ptype)

        #one to one mappings
        for k in ['title', 'volume', 'issue']:
            bib[k] = pull(meta, k)

        bib['pages'] = pull(meta, 'page')

        #author list
        bib['authors'] = self._author_list(meta)

        #contributors
        contrib = []
        for ct in contributors:
            contrib.append(ct)
        bib['contributor'] = contrib


        #date
        date = self._pub_date(meta)
        try:
            bib['date'] = date
        except Exception, e:
            logging.warn("Can't create date for {0}.".format(doi))
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

    def to_json(self, doi):
        """
        Helper to process a DOI and conver to local JSON.
        """
        raw = self.fetch(doi)
        meta = self.prep(raw)
        return meta

    def to_graph(self, prepped):
        g = to_rdf(prepped, Graph())
        return g


