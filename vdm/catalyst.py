"""
Client for services from the Harvard Catalyst project.
http://profiles.catalyst.harvard.edu/docs/ProfilesRNS_DisambiguationEngine.pdf
"""
import xml.etree.cElementTree as ET

import requests

import logging
logger = logging.getLogger(__name__)

class DisambiguationEngine(object):
    """
    Make and post documents to the disambiguation engine.
    http://profiles.catalyst.harvard.edu/docs/ProfilesRNS_DisambiguationEngine.pdf
    """
    def __init__(self):
        self.threshold_score = '0.98'
        self.affiliation_strings = []
        self.require_first_name = 'false'

    def do(self, *args):
        """
        Helper to call the service with the given args.
        """
        doc = self.build_doc(*args)
        pubs = self.post(doc)
        return pubs

    def post(self, xml):
        """
        Post the given doc to the service and get back
        a list of Pubmed IDs.
        """
        url = 'http://profiles.catalyst.harvard.edu/services/GetPMIDs/default.asp'
        headers = {'Content-Type': 'text/xml'}
        resp = requests.post(url, data=xml, headers=headers)
        logger.debug("Disambiguation service status code.", resp.status_code)
        root = ET.fromstring(resp.text)
        publications = []
        for child in root:
            publications.append(child.text)
        return publications

    def build_doc(self,
            first_name,
            last_name,
            middle_name,
            primary_email,
            known_pubs,
            exclude_pubs):
        """
        See structure at above url.
        """
        root = ET.Element("FindPMIDs")
        name = ET.SubElement(root, "Name")
        if (first_name is None) or (last_name is None):
            raise Exception("First and last name required.")
        first = ET.SubElement(name, "First")
        first.text = first_name
        if middle_name is not None:
            middle_elem = ET.SubElement(name, "Middle")
            middle_elem.text = middle_name
        last = ET.SubElement(name, "Last")
        last.text = last_name
        #email
        email_elem = ET.SubElement(root, "EmailList")
        primary_email_elem = ET.SubElement(email_elem, "email")
        primary_email_elem.text = primary_email
        #Affiliations
        affiliation = ET.SubElement(root, "AffiliationList")
        for aff in self.affiliation_strings:
            chunk = ET.SubElement(affiliation, "Affiliation")
            chunk.text = "%{0}%".format(aff)
        #ToDo: figure out what this means/does
        dups = ET.SubElement(root, "LocalDuplicateNames")
        dups.text = '1'
        #Pass this in from profile depending on fac
        require_first = ET.SubElement(root, "RequireFirstName")
        require_first.text = self.require_first_name
        #Pass this in from profile depending on fac
        threshold = ET.SubElement(root, "MatchThreshold")
        threshold.text = self.threshold_score
        if known_pubs is None:
            raise Exception("Known PMIDs are required.")
        pmid_add = ET.SubElement(root, "PMIDAddList")
        for pub in known_pubs:
            padd = ET.SubElement(pmid_add, "PMID")
            padd.text = pub
        pmid_exclude = ET.SubElement(root, "PMIDExcludeList")
        for pub in exclude_pubs:
            padd = ET.SubElement(pmid_exclude, "PMID")
            padd.text = pub
        return ET.tostring(root)
