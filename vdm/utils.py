import os

import bleach


def get_env(name):
    val = os.getenv(name)
    if val is None:
        raise Exception("Can't find envrionment variable {}.".format(name))
    return val

def scrub_doi(val):
    """
    Get only the DOI.  Not other stuff.
    """
    v = val.replace('http://dx.doi.org/', '')
    v = v.replace('dx.doi.org/', '')
    v = v.replace('doi:', '')
    v = bleach.clean(v)
    v = v.replace(' ', '')
    return v.strip()

def pull(meta):
    f = lambda x: None if x is u'' else x
    return f(meta)