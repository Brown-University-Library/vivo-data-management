import logging
logger = logging.getLogger(__name__)

from datetime import date
import json
import xml.etree.ElementTree as ET

import requests

from rdflib import Graph

from rdflib_jsonld.parser import to_rdf

from . import context

from .utils import pull, get_user_agent, scrub_doi

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
    print(handle.request.headers)
    try:
        graph = Graph().parse(data=handle.text)
    except Exception as e:
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
    except Exception as e:
        logger.error("Bad DOI {0}".format(doi))
        logger.error(e)
        return


class CrossRefSearchException(Exception):
    pass


def metadata_search(search_string):
    """
    Search the metadata API.

    Updated 7/3/2019
    CrossRef search API no longer functioning.
    Repurposing DOI resolution as DOI search.
    """
    try:
        pub = Publication()
        prepped = pub.to_json(scrub_doi(search_string))
        full_citation = ''
        if isinstance(prepped['title'], list):
            full_citation += '<em>{}</em>'.format(prepped['title'][0])
        elif isinstance(prepped['title'], str):
            full_citation += '<em>{}</em>'.format(prepped['title'])
        else:
            raise CrossRefSearchException("Citation has no title. Exiting")
        if prepped['date']:
            full_citation += '. {}'.format(prepped['date'].year)
        return [ {'doi': prepped['doi'], 'fullCitation': full_citation }]
    except Exception as e:
        logging.error(e)
        raise CrossRefSearchException("Failure to parse CR results")


class Publication:

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
        if ptype == 'journal-article':
            d['a'] = 'bcite:Article'
        elif (ptype == 'Book') or (ptype == 'Monograph'):
            d['a'] = 'bcite:Book'
        #add to bcite ontology
        elif ptype == 'proceedings-article':
            d['a'] = 'bcite:ConferencePaper'
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
        except Exception as e:
            logging.warn("Can't create date for {0}.".format(doi))
            logging.warn(e)

        #venue
        venue = {}
        if venue_uri is not None:
            venue['uri'] = venue_uri
        venue['label'] = pull(meta, 'container-title')
        venue['issn'] = pull(meta, 'ISSN')
        venue['isbn'] = pull(meta, 'ISBN')
        venue['a'] = 'bcite:Venue'
        bib['venue'] = venue
        bib['published_in'] = pull(meta, 'container-title')

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


def by_openurl(ourl_params, email):
    """
    Lookup the DOI from CrossRef given OpenURL metdata.
    http://labs.crossref.org/openurl/

    Requires an API key, which is the registered user's email.

    Experience shows these fields are minimally required for articles:
        - issn
        - year
        - spage (start page for article)
        - volume or issue
    """
    cr_url = 'http://crossref.org/openurl/'
    payload = {
        'pid': email,
        'format': 'unixref',
        'noredirect': 'true',
    }
    #Add incoming parameters
    payload.update(ourl_params)
    logger.debug("CrossRef url {} with params {}".format(cr_url, json.dumps(payload)))
    resp = requests.get(cr_url, params=payload)
    try:
        root = ET.fromstring(resp.text.encode('utf-8', 'ignore'))
    except UnicodeEncodeError:
        logger.info("Error parsing CR response")
        return
    title_elem = root.find('./doi_record/crossref/journal/journal_article/titles/title')
    if title_elem is None:
        return
    cr_title = title_elem.text
    doi_node = root.findall('./doi_record/crossref/journal/journal_article/doi_data/doi')
    try:
        doi = doi_node[0].text
    except IndexError:
        logger.info("Error parsing DOI from CR response.")
        return
    return (cr_title, doi)
