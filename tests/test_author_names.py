import unittest

from vdm.author_names import Author, catalyst_match, chunk_name

fac_1 = f = Author(
    #uri=u'http://example.org/fac1',
    full=u'smith, john d.',
    last=u'smith',
    first=u'john',
    first_initial=u'j',
    middle=u'd',
    middle_initial=u'd'
)


fac_2 = f = Author(
    #uri=u'http://example.org/fac2',
    full=u'weber, griffin m.',
    last=u'weber',
    first=u'griffin',
    first_initial=u'g',
    middle=u'm',
    middle_initial=u'm'
)

class TestCatalystMatch(unittest.TestCase):
    """
    Test cases from here:
    http://profiles.catalyst.harvard.edu/Meetings/ProfilesRNSDisambiguation120120.pdf
    """

    def test_match_fac1(self):
        test_cases = [
            u"J. D. Smith",
            u"John David Smith",
            u"J. Daniel Smith",
            u"J. Smith",
        ]
        for name in test_cases:
            au = chunk_name(name)
            assert catalyst_match(au, fac_1) is True

    def test_no_match_fac1(self):
        test_cases = [
            u"Jonathan D. Smith",
            #Typo intentional
            u"John D. Smtih",
            u"James Smith",
            u"John D. Smithers",
        ]
        for name in test_cases:
            au = chunk_name(name)
            assert catalyst_match(au, fac_1) is False

    def test_match_fac2(self):
        test_cases = [
            u"G Weber",
            u"G M Weber",
            u"Griffin Weber",
            u"Griffin M Weber",
        ]
        for name in test_cases:
            au = chunk_name(name)
            assert catalyst_match(au, fac_2) is True

    def test_no_match_fac2(self):
        test_cases = [
            u"G T Weber",
            #Two bs in Weber.
            u"G Webber",
            u"Griffin X Weber",
        ]
        for name in test_cases:
            au = chunk_name(name)
            assert catalyst_match(au, fac_2) is False


class TestChunkWokName(unittest.TestCase):

    def test_first_middle_last(self):
        nm = u"Jonathan D. Smith"
        au = chunk_name(nm)
        assert au.first == u"jonathan"
        assert au.middle == u"d"
        assert au.last == u"smith"