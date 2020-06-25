
import os
import unittest

import json

#Directory where test data is stored.
DATA_PATH = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'data'
)

def load(fname):
    with open(os.path.join(DATA_PATH, fname)) as f:
        return json.load(f)

class BTest(unittest.TestCase):
    def eq(self, v1, v2):
        self.assertEqual(v1, v2)


CROSSREF_OPENURL_RESPONSE = '''<?xml version="1.0" encoding="UTF-8"?>
<doi_records>
  <doi_record key="555-555" owner="10.1007" timestamp="2014-12-19 10:31:42">
    <crossref>
      <journal>
        <journal_metadata language="en">
          <full_title>Extremophiles</full_title>
          <abbrev_title>Extremophiles</abbrev_title>
          <issn media_type="print">1431-0651</issn>
          <issn media_type="electronic">1433-4909</issn>
        </journal_metadata>
        <journal_issue>
          <publication_date media_type="print">
            <month>1</month>
            <year>2015</year>
          </publication_date>
          <journal_volume>
            <volume>19</volume>
          </journal_volume>
          <issue>1</issue>
        </journal_issue>\r\n
        <journal_article publication_type="full_text">
          <titles>
            <title>Transposon mutagenesis of the extremely thermophilic bacterium Thermus thermophilus HB27</title>
          </titles>
          <contributors>
            <person_name contributor_role="author" sequence="first">
              <given_name>Jennifer F.</given_name>
              <surname>Carr</surname>
            </person_name>
            <person_name contributor_role="author" sequence="additional">
              <given_name>Steven T.</given_name>
              <surname>Gregory</surname>
            </person_name>
            <person_name contributor_role="author" sequence="additional">
              <given_name>Albert E.</given_name>
              <surname>Dahlberg</surname>
            </person_name>
          </contributors>
          <publication_date media_type="online">
            <month>6</month>
            <day>20</day>
            <year>2014</year>
          </publication_date>
          <publication_date media_type="print">
            <month>1</month>
            <year>2015</year>
          </publication_date>
          <pages>
            <first_page>221</first_page>
            <last_page>228</last_page>
          </pages>
          <publisher_item>
            <identifier id_type="pii">663</identifier>
          </publisher_item>
          <crossmark>
            <crossmark_version>1</crossmark_version>
            <crossmark_policy>10.1007/springer_crossmark_policy</crossmark_policy>
            <crossmark_domains>
              <crossmark_domain>
                <domain>link.springer.com</domain>
              </crossmark_domain>
            </crossmark_domains>
            <crossmark_domain_exclusive>false</crossmark_domain_exclusive>
          </crossmark>
          <doi_data>
            <doi>10.1007/s00792-014-0663-8</doi>
            <timestamp>20141219163109</timestamp>
            <resource>http://link.springer.com/10.1007/s00792-014-0663-8</resource>
            <collection property="crawler-based" setbyID="springer">
              <item crawler="iParadigms">
                <resource>http://link.springer.com/content/pdf/10.1007/s00792-014-0663-8</resource>
              </item>
            </collection>
          </doi_data>
        </journal_article>
      </journal>
    </crossref>
  </doi_record>
</doi_records>'''
