import json
import logging

from pprint import pprint

from dateutil.parser import parse

from rdflib import Graph
from rdflib import Namespace

from rdflib_jsonld.parser import to_rdf

import requests
#Cache if we can
try:
    import requests_cache
    requests_cache.install_cache('/tmp/vdm_cache.sqlite')
except ImportError:
    pass


D = Namespace('http://vivo.brown.edu/individual/')

#from context import base, publication, publication_venue
import context

from utils import pull

def get_pubmed(id):
    doc_url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=%s&retmode=json' % pmid
    resp = requests.get(doc_url)
    raw = resp.json()
    if raw is not None:
        meta = raw['result'][pmid]
        return meta
    else:
        raise Exception("No PMID found with this ID {}.".format(doc_url))

class Pubmed(object):
    def __init__(self, pmid):
        self.id = pmid

    def fetch(self):
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

        #date
        spdate = bib.get('sortpubdate')
        if spdate is not None:
            bib['date'] = parse(spdate).isoformat()

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

if __name__ == "__main__":
    from rdflib import Graph, BNode
    g = Graph()
    log = logging.getLogger(__name__)
    to_check = [
        '6869634',
        '9285281',
        '8996046',
        '23748631',
        '23910982',
        '19653787',
        '21928871'
    ]
    pubs = []
    for count, pmid in enumerate(to_check):
        meta = get_pubmed(pmid)
        bib = {}
        bib['uri'] = 'p' + str(count)
        #One to one mappings
        for k in ['title', 'volume', 'issue', 'pages']:
            bib[k] = pull(meta.get(k))

        #handle authors
        authors = []
        for au in meta['authors']:
            authors.append(au['name'])
        bib['authors'] = u", ".join(authors)

        pub_context.update(base_context)
        pub_context.update(venue_context)
        bib['@context'] = pub_context
        pprint(bib)

        #date
        spdate = bib.get('sortpubdate')
        if spdate is not None:
            bib['date'] = parse(spdate).isoformat()

        venue = {}
        venue['label'] = meta['fulljournalname']
        venue['issn'] = pull(meta.get('issn'))
        venue['eissn'] = pull(meta.get('essn'))
        venue['uri'] = 'n' + str(count)
        bib['venue'] = venue

        #brown - contributors
        #bib['contributor'] = ['akane', 'vmor']
        pubs.append(bib)

    #g = jldg(pubs)
    g = to_rdf(pubs, g)
    g.namespace_manager = ns_mgr
    print g.serialize(format='turtle')


    # #some aliases
    # BASE_CONTEXT = {
    #     "a": "@type",
    #     "uri": "@id",
    #     "title": "rdfs:label",
    # }

    # def jldg(doc):
    #     """
    #     Return a Python Graph object from
    #     a jsonld context and graph.
    #     """
    #     from rdflib import Graph
    #     raw_jld = json.dumps(doc, indent=2)
    #     g = Graph().parse(data=raw_jld, format='json-ld')
    #     return g

    # def jld(context, doc, include_common=True, base=None):
    #     from vdm.models import BU as D
    #     from vdm.models import ns_mgr
    #     if include_common is True:
    #         context.update(BASE_CONTEXT)
    #     if base is None:
    #         context['@base'] = D
    #     #set namespaces
    #     for prefix, iri in ns_mgr.namespaces():
    #         context[prefix] = iri.toPython()
    #     #To transform
    #     d = {'@context': context}
    #     d.update(doc)
    #     return d
    # ctx = {
    #     'pmid': 'bcite:pmid',
    #     'doi': 'bcite:doi',
    #     "authors": "bcite:authorList",
    #     "venue": {
    #         "@id": "bcite:hasVenue",
    #         "@type": "@id",
    #     }
    # }
    # venue_ctx = {
    #     'issn': 'bcite:issn',
    #     'eissn': 'bcite:eissn',
    # }
    # outg = Graph()
    # for pmid in to_check:
    #     # d = to_bibjson(pm)
    #     # uri, g = to_bcite(d)
    #     # print g.serialize(format='n3')
    #     # print
    #     doc_url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=%s&retmode=json' % pmid
    #     resp = requests.get(doc_url)
    #     raw = resp.json()
    #     if raw is not None:
    #         meta = raw['result'][pmid]
    #     else:
    #         raise Exception("No PMID found with this ID {}.".format(doc_url))

    #     bib = {}
    #     bib['uri'] = "pmid{}".format(pmid)

    #     f = lambda x: None if x is u'' else x
    #     #Handle venue
    #     #Write a merge routine to merge venues as soon as they are added.
    #     #Could also handle types.
    #     venue = {}
    #     venue['a'] = 'bcite:Venue'
    #     venue['uri'] = 'venue' + pmid
    #     venue['title'] = meta.get('fulljournalname')
    #     venue['issn'] = meta.get('issn')
    #     venue['eissn'] = f(meta.get('essn'))
    #     d = jld(venue_ctx, venue)
    #     outg += jldg(d)

    #     bib['venue'] = venue['uri']

    #     #One to one mappings.
    #     for k in ['title', 'volume', 'issue', 'pages']:
    #         bib['bcite:{}'.format(k)] = meta.get(k)
    #     #Handle ids.
    #     for aid in meta.get('articleids', []):
    #         idtype = aid['idtype']
    #         value = aid['value']
    #         if idtype == 'pubmed':
    #             bib['pmid'] = value
    #         elif idtype == 'doi':
    #             bib['doi'] = value
    #     #Do type.
    #     ptypes = meta['pubtype']
    #     for ptype in meta.get('pubtype', []):
    #         if ptype == 'Journal Article':
    #             bib['a'] = "bcite:Article"
    #         #One to one.
    #         elif ptype in ['Review']:
    #             bib['a'] = 'bcite:' + ptype
    #         else:
    #             print '***', ptype
    #             bib['a'] = "bcite:Citation"
    #     author_list = ', '.join([au['name'] for au in meta['authors']])
    #     bib['authors'] = author_list
    #     d = jld(ctx, bib)
    #     outg += jldg(d)

    # from pprint import pprint
    # pprint(d)
    # print outg.serialize(format='n3')