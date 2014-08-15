
import re
import os

import bleach


def get_env(name):
    val = os.getenv(name)
    if val is None:
        raise Exception("Can't find environment variable {0}.".format(name))
    return val

def remove_html(text):
    """
    Using bleach remove all HTML markup from text.
    http://bleach.readthedocs.org/en/latest/clean.html#stripping-markup
    """
    return bleach.clean(text, strip=True, tags=[])

def scrub_doi(val):
    """
    Get only the DOI.  Not other stuff.
    """
    #Remove html
    v = remove_html(val)
    #lower case
    v = v.lower()
    v = v.replace('http://dx.doi.org/', '')
    v = v.replace('dx.doi.org/', '')
    #leading DOI prefiex
    v = v.replace('doi:', '')
    v = v.replace(' ', '')
    return v.strip()

def pull(meta, k):
    f = lambda x: None if unicode(x) is u'' else x
    return f(meta.get(k))


def get_user_agent():
    """
    Utility to get user agent for requests library.
    """
    try:
        agent = get_env('VDM_USER_AGENT')
        return {'User-Agent': agent}
    except Exception:
        #No agent set
        return {}

def scrub_pmid(value):
    """
    Minimal cleanup on incoming PMIDs for validation.
    http://www.nlm.nih.gov/bsd/mms/medlineelements.html#pmid
    """
    if value.startswith("PMC"):
        return None
    match = re.findall(r'([1-9]{1}\d{2,7})', value)
    try:
        v = match[0]
    except IndexError:
        return None
    #Don't allow 0 to be returned.
    if v == 0:
        return None
    return v
