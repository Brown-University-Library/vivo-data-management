# vivo-data-management

Python and RDFLib tools for managing data for [VIVO](http://vivoweb.org).

![Build Status](https://github.com/Brown-University-Library/vivo-data-management/actions/workflows/ci.yml/badge.svg)

## Overview

This library packages commonly used tools for managing VIVO data at Brown.

Including:

 - CrossRef search api
 - CrossRef lookup by [OpenURL](http://labs.crossref.org/openurl/) (requires key)
 - [Profiles Research Networking Software (RNS) Disambiguation Engine](http://profiles.catalyst.harvard.edu/docs/ProfilesRNS_DisambiguationEngine.pdf) from the Harvard Catalyst project
 -  Pubmed API
 - Pubmed [ID Converter API](https://www.ncbi.nlm.nih.gov/pmc/tools/id-converter-api/)
 - Text processing utilities for matching author names
 - [Vitro/VIVO SPARQL Update API](https://wiki.duraspace.org/display/VIVO/The+SPARQL+Update+API) client

## Installation

Use [pip](https://pypi.python.org/pypi/pip) to install directly from Github.

`$ pip install git+https://github.com/Brown-University-Library/vivo-data-management.git`

This has been developed and tested with Python 2.7.

## Development

### Running tests

The tests are written with [pytest](http://pytest.org/latest/) and expect a default namespace.  Run with:

`$ DATA_NAMESPACE='http://vivo.school.edu/individual/' py.test`
