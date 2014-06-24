

import pytest


def test_scrub_doi():
    from vdm.utils import scrub_doi
    d = 'http://dx.doi.org/10.1234'
    scrubbed = scrub_doi(d)
    assert(scrubbed == '10.1234')

    d = '10.123 4'
    assert(
        scrub_doi(d) == '10.1234'
    )

    d = '<p>10.1234</p>'
    assert(
        scrub_doi(d) == '10.1234'
    )


def test_pull():
    from vdm.utils import pull
    d = {}
    d['mykey'] = 'Value'
    assert(
        pull(d, 'mykey') == 'Value'
    )
    d['key2'] = ''
    assert(
        pull(d, 'key2') is None
    )
    d['key3'] = u''
    assert(
        pull(d, 'key3') is None
    )


def test_get_env():
    from vdm.utils import get_env
    import os
    os.environ['TMP'] = 'pytest'
    assert(
        get_env('TMP') == 'pytest'
    )
    os.environ.pop('TMP')
    with pytest.raises(Exception):
        get_env('TMP')
