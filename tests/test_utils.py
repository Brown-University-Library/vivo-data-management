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

    d = '<a href="http://dx.doi.org/10.1234">10.1234</a>'
    assert(
        scrub_doi(d) == '10.1234'
    )

    d = 'DOI:10.1234'
    assert (
        scrub_doi(d) == '10.1234'
    )

    d = 'doi:10.1234'
    assert (
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


def test_remove_html():
    from vdm.utils import remove_html

    t = "<h1>hello</h1>"
    assert(
        remove_html(t),
        'hello'
    )
    t = "<div><h1>hello</h1><span class=\"blah\">world</span></div>"
    assert(
        remove_html(t),
        'hello world'
    )

def test_user_agent():
    """
    Set user agent.
    """
    from vdm.utils import setup_user_agent
    import os
    import requests
    agent = "Sample agent"
    os.environ['USER_AGENT'] = agent
    h = setup_user_agent()
    resp = requests.get('http://httpbin.org/get', headers=h)
    assert(resp.request.headers.get('User-Agent') == agent)

def test_user_agent_warning():
    """
    No user agent set should trigger a warning.
    """
    from vdm.utils import setup_user_agent
    import os
    import warnings
    with warnings.catch_warnings(record=True) as w:
        os.environ.pop('USER_AGENT')
        #This should trigger a warning.
        headers = setup_user_agent()
        assert "agent" in str(w[-1].message)
        assert issubclass(w[-1].category, UserWarning)
