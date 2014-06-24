import logging
logger = logging.getLogger(__name__)

from dateutil.parser import parse

from rdflib import Graph

from rdflib_jsonld.parser import to_rdf

import requests
#Cache if we can
try:
    import requests_cache
    requests_cache.install_cache('/tmp/vdm_cache.sqlite')
except ImportError:
    pass


#from context import base, publication, publication_venue
import context

from utils import pull

def get_pubmed(pmid):
    doc_url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=%s&retmode=json' % pmid
    resp = requests.get(doc_url)
    raw = resp.json()
    if raw is not None:
        meta = raw['result'][pmid]
        return meta
    else:
        raise Exception("No PMID found with this ID {}.".format(doc_url))

class Pubmed(object):
    def __init__(self):
        pass

    def fetch(self, pmid):
        doc_url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=%s&retmode=json' % pmid
        resp = requests.get(doc_url)
        raw = resp.json()
        if raw is not None:
            meta = raw['result'][pmid]
            return meta
        else:
            raise Exception("No PMID found with this ID {}.".format(doc_url))

    def pub_types(self, meta):
        d = {}
        for ptype in meta.get('pubtype', []):
            if ptype == u'Journal Article':
                d['a'] = "bcite:Article"
                return d
            #One to one.
            elif ptype in [u'Review']:
                d['a'] = 'bcite:' + ptype
                return d
            else:
                d['a'] = "bcite:Citation"
        return d

    def date(self, meta):
        #date
        spdate = meta.get('sortpubdate')
        if spdate is not None:
            return parse(spdate).isoformat()
        return

    def prep(self, meta, pub_uri=None, venue_uri=None):
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
            bib[k] = pull(meta.get(k))
        #Identifiers
        for aid in meta.get('articleids', []):
            value = pull(aid.get('value'))
            id_type = aid.get('idtype')
            if id_type == 'pubmed':
                bib['pmid'] = value
            elif id_type == 'doi':
                bib['doi'] = value
            elif id_type == 'pmc':
                bib['pmcid'] = value

        #Handle author list
        authors = []
        for au in meta['authors']:
            authors.append(au['name'])
        bib['authors'] = u", ".join(authors)

        bib['date'] = self.date(meta)

        venue = {}
        if venue_uri is not None:
            venue['uri'] = venue_uri
        venue['label'] = meta['fulljournalname']
        venue['issn'] = pull(meta.get('issn'))
        venue['eissn'] = pull(meta.get('essn'))
        bib['venue'] = venue

        c = {}
        c.update(context.base)
        c.update(context.publication)
        bib['@context'] = c
        return bib

    def to_graph(self, prepped):
        g = to_rdf(prepped, Graph())
        return g

