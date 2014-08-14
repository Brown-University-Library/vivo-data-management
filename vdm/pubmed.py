import logging
logger = logging.getLogger(__name__)

from dateutil.parser import parse

from rdflib import Graph

from rdflib_jsonld.parser import to_rdf

import requests

#from context import base, publication, publication_venue
import context

from utils import pull, get_user_agent


def get_pubmed(pmid):
    ua = get_user_agent()
    doc_url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=%s&retmode=json' % pmid
    resp = requests.get(doc_url, headers=ua)
    raw = resp.json()
    if raw is not None:
        meta = raw['result'][pmid]
        return meta
    else:
        raise Exception("No PMID found with this ID {0}.".format(doc_url))

class Publication(object):
    def __init__(self):
        pass

    def fetch(self, pmid):
        doc_url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=%s&retmode=json' % pmid
        ua = get_user_agent()
        resp = requests.get(doc_url, headers=ua)
        raw = resp.json()
        if raw.get('error') is None:
            meta = raw['result'][pmid]
            return meta
        else:
            raise Exception("No PMID found with this ID {0}.".format(doc_url))

    def pub_types(self, meta):
        d = {}
        for ptype in meta.get('pubtype', []):
            if ptype in [u'Review']:
                d['a'] = 'bcite:' + ptype
                return d
            elif ptype == u'Journal Article':
                d['a'] = "bcite:Article"
                return d
            #One to one.
            else:
                d['a'] = "bcite:Citation"
        #Check doctype for book.
        if meta.get('doctype') == u"book":
            d['a'] = 'bcite:Book'
        if meta.get('doctype') == u"chapter":
            d['a'] = 'bcite:BookSection'
        return d

    def date(self, meta):
        """
        Handle publication dates.
        """
        spdate = meta.get('sortpubdate')
        if spdate is not None:
            dt = parse(spdate)
            #Only date not datetime needed.
            return dt.date()
        return

    def prep(self, meta, pub_uri=None, venue_uri=None, contributors=[]):
        """
        Create JSON to pass to the context.
        """
        bib = {}
        if pub_uri is not None:
            bib['uri'] = pub_uri
        #pub type
        ptype = self.pub_types(meta)
        bib.update(ptype)
        #One to one mappings
        for k in ['title', 'volume', 'issue', 'pages']:
            bib[k] = pull(meta, k)
        #For books, the title is in booktitle.
        if bib.get('title') is None:
            bib['title'] = pull(meta, 'booktitle')
        #Identifiers
        for aid in meta.get('articleids', []):
            value = pull(aid, 'value')
            id_type = aid.get('idtype')
            if id_type == 'pubmed':
                bib['pmid'] = value
            elif id_type == 'doi':
                bib['doi'] = value
            elif id_type == 'pmc':
                bib['pmcid'] = value

        #Handle author list
        authors = []
        for au in meta.get('authors', []):
            authors.append(au['name'])
        bib['authors'] = u", ".join(authors)

        #contributors
        contrib = []
        for ct in contributors:
            contrib.append(ct)
        bib['contributor'] = contrib

        bib['date'] = self.date(meta)

        #Get venues if there is one.
        venue = {}
        if venue_uri is not None:
            venue['uri'] = venue_uri
        venue['label'] = pull(meta, 'fulljournalname')
        venue['issn'] = pull(meta, 'issn')
        venue['eissn'] = pull(meta, 'essn')
        if (venue['label'] is not None):
            bib['venue'] = venue

        #Check for book 
        book = pull(meta, 'booktitle')
        if book is not None and bib.get('title') is not None:
            bib['book'] = book
        #Check for urls
        url = pull(meta, 'availablefromurl')
        if url is not None:
            bib['url'] = url
        
        c = {}
        c.update(context.base)
        c.update(context.publication)
        bib['@context'] = c
        return bib

    def to_json(self, pmid):
        """
        Helper to process a PMID and conver to local JSON.
        """
        raw = self.fetch(pmid)
        meta = self.prep(raw)
        return meta

    def to_graph(self, prepped):
        g = to_rdf(prepped, Graph())
        return g


def id_convert(values, idtype=None):
    """
    Get data from the id converter API.
    https://www.ncbi.nlm.nih.gov/pmc/tools/id-converter-api/
    """
    base = 'http://www.pubmedcentral.nih.gov/utils/idconv/v1.0/'
    ua = get_user_agent()
    params = {
        'ids': values,
        'format': 'json',
    }
    if idtype is not None:
        params['idtype'] = idtype

    #Make request with user agent.
    resp = requests.get(base, params=params, headers=ua)
    raw = resp.json()
    records = raw.get('records')
    if records is None:
        return None
    status = records[0].get('status')
    if status == u"error":
        return None

    return raw['records'][0]


def doi_search(doi):
    """
    Search Pubmed by DOI to get a Pubmed ID.

    For some reason, this returns more results than above.
    """
    if doi is None:
        raise Exception("No DOI passed to search.")
    base = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={}[doi]&retmode=json"
    surl = base.format(doi)
    ua = get_user_agent()
    #Make request with user agent.
    resp = requests.get(surl, headers=ua)
    raw = resp.json()
    results = raw.get('esearchresult')
    if results is not None:
        id_list = results.get('idlist')
        if id_list is None:
            return None
        elif len(id_list) > 1:
            raise Exception("Multiple PMID ids returned for Pubmed DOI search.")
        else:
            return id_list[0]
    return None



