"""
JSON-LD contexts.
"""
from .namespaces import ns_mgr, D

base = {
    "@base": str(D),
    "a": "@type",
    "uri": "@id",
    "label": "rdfs:label",
}

#set namespaces from the ns_mgr
for prefix, iri in ns_mgr.namespaces():
    base[prefix] = iri.toPython()

#BCITE publications
publication = {
    "title": "rdfs:label",
    "authors": "bcite:authorList",
    'pmid': 'bcite:pmid',
    'doi': 'bcite:doi',
    "pmcid": "bcite:pmcid",
    "issue": "bcite:issue",
    "volume": "bcite:volume",
    "issn": "bcite:issn",
    "eissn": "bcite:eissn",
    "book": "bcite:book",
    "published_in": "bcite:publishedIn",
    "date": {
        "@id": "bcite:date",
        "@type": "http://www.w3.org/2001/XMLSchema#date"
    },
    "url": "bcite:url",
    "pages": "bcite:pages",
    "venue": {
        "@id": "bcite:hasVenue",
        "@type": "@id",
    },
    "contributor": {
        "@id": "bcite:hasContributor",
        "@type": "@id",
    }
}

#Brown delegate editors
delegate = {
    "first": "foaf:firstName",
    "last": "foaf:lastName",
    "short_id": "blocal:shortId",
    "ou": "blocal:orgUnit",
    "netId": "blocal:netId",
}

