# -*- coding: utf-8 -*-
from vdm.text import normalize, tokenize, url_slug, clean_parens


def test_normalize():
    #Mixed case and str to unicode
    assert normalize('BroWn') == normalize(u'Brown')
    #Trailing spaces
    assert normalize('  Brown  ') == normalize('Brown')
    #removed accents
    assert normalize(u'Èasy') == normalize('Easy')
    #new lines
    assert normalize('Brown\nUniv') == normalize('brown univ')


def test_tokenize():
    tokens = [t for t in tokenize("Brown Univ.")]
    assert tokens == ['Brown', 'Univ']
    tokens = [t for t in tokenize("Brown Univ.02912")]
    assert '02912' in tokens


def test_url_slug():
    assert url_slug('Brown Univ') == 'brown-univ'
    assert url_slug('Brown univ') == 'brown-univ'
    assert url_slug('Brown.Univ') == 'brown_univ'


def test_clean_parens():
    assert clean_parens('Brown Univ (US)') == 'brown univ'
    assert clean_parens('Brown Univ (US)', normalized=False) == 'Brown Univ'