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
    from vdm.utils import get_user_agent
    import os
    import requests
    agent = "Sample agent"
    os.environ['VDM_USER_AGENT'] = agent
    h = get_user_agent()
    resp = requests.get('http://httpbin.org/get', headers=h)
    assert(resp.request.headers.get('User-Agent') == agent)
    del os.environ['VDM_USER_AGENT']

def test_user_agent_not_set():
    """
    No user agent set should trigger a warning.
    """
    from vdm.utils import get_user_agent
    import os
    import requests
    #This will cause warnings to raise an error
    try:
        del os.environ['VDM_USER_AGENT']
    except KeyError:
        pass
    headers = get_user_agent()
    assert headers == {}
    resp = requests.get('http://httpbin.org/get', headers=headers)
    #By default the user agent will contain python.
    assert(resp.request.headers.get('User-Agent').find('python') > -1)


def test_scrub_pmid():
    from vdm.utils import scrub_pmid
    assert scrub_pmid(u'PMC2727248') is None
    p = u'18633329'
    assert scrub_pmid(p) == p
    assert(scrub_pmid(u'000') is None)

    #7 digit pmid ids
    assert(
        scrub_pmid(u'8013034') == u'8013034'
    )

    assert(
        scrub_pmid(u'9059992') == u'9059992'
    )

