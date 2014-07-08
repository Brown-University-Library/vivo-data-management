import pytest
from vdm.catalyst import DisambiguationEngine

from vdm.utils import get_env

try:
    get_env('TRAVIS')
    TRAVIS = True
except Exception:
    TRAVIS = False

def test_profile():
    #Basic info about a person.
    p = [
        'Josiah',
        'Carberry',
        None,
        'jcarberry@brown.edu',
        ['null'],
        ['null']
    ]

    disambig = DisambiguationEngine()
    disambig.affiliation_strings = ['Sample University']

    doc = disambig.build_doc(*p)

    #Basic verification that XML contains what we expect.
    assert('<First>Josiah</First>' in doc)
    assert('<Last>Carberry</Last>' in doc)
    assert('<email>jcarberry@brown.edu</email>' in doc)
    assert('<Affiliation>%Sample University%</Affiliation>' in doc)

@pytest.mark.skipif(TRAVIS is True, reason="run locally")
def test_engine():
    p = [
        'Griffin',
        'Webber',
        'M',
        'weber@hms.harvard.edu',
        ['11707567', '12209713', '16359929'],
        ['19648504']
    ]
    disambig = DisambiguationEngine()
    disambig.affiliation_strings = ['harvard medical school', 'Massachusetts General', 'Brigham Women']
    returned = disambig.do(*p)
    expected = ['11707567', '12209713', '16359929']
    #Make sure expected pubs are in returned.
    #assert (set(expected).issubset(set(returned)) is True)
    for pmid in expected:
        assert(pmid in returned)

@pytest.mark.skipif(TRAVIS is True, reason="run locally")
def test_post():
    doc = """
    <FindPMIDs>
         <Name>
         <First>Griffin</First>
         <Middle>M</Middle>
         <Last>Weber</Last>
         <Suffix />
         </Name>
         <EmailList>
         <email>weber@hms.harvard.edu</email>
         <email>weber@fas.harvard.edu</email>
         </EmailList>
         <AffiliationList>
         <Affiliation>%harvard medical school%</Affiliation>
         <Affiliation>%Massachusetts General%</Affiliation>
         <Affiliation>%Brigham%Women%</Affiliation>
         <Affiliation>%@hms.harvard.edu%</Affiliation>
         </AffiliationList>
         <LocalDuplicateNames>1</LocalDuplicateNames>
         <RequireFirstName>false</RequireFirstName>
         <MatchThreshold>0.98</MatchThreshold>
         <PMIDAddList>
         <PMID>11707567</PMID>
         <PMID>12209713</PMID>
         <PMID>16359929</PMID>
         </PMIDAddList>
         <PMIDExcludeList>
         <PMID>19648504</PMID>
         </PMIDExcludeList>
    </FindPMIDs>
    """
    disambig = DisambiguationEngine()
    returned = disambig.post(doc)
    expected = ['11707567', '12209713', '16359929']
    for pmid in expected:
        assert(pmid in returned)

def test_prep_returned_list():
    response = """
    <PMIDList><PMID>11707567</PMID><PMID>12209713</PMID></PMIDList>
    """
    disambig = DisambiguationEngine()
    pub_list = disambig.prep_returned_list(response)
    assert(
        pub_list\
        ==\
        ['11707567', '12209713']
    )
