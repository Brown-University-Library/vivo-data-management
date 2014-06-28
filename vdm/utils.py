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
    f = lambda x: None if str(x) is '' else x
    return f(meta.get(k))