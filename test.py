#! /usr/bin/env python3
"""
Some basic unit tests.
"""

import unittest

import example_ncbi as example

class TestNcbiExample(unittest.TestCase):
    """
    """
    def test_xml_parsing(self):
        """
        Test parsing of XML returned by NCBI's esearch
        """
        xml = """<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE eSearchResult PUBLIC "-//NLM//DTD esearch 20060628//EN" "https://eutils.ncbi.nlm.nih.gov/eutils/dtd/20060628/esearch.dtd">
<eSearchResult><Count>1</Count><RetMax>1</RetMax><RetStart>0</RetStart><IdList>
<Id>672</Id>
</IdList><TranslationSet><Translation>     <From>Homo sapiens[organism]</From>     <To>"Homo sapiens"[Organism]</To>    </Translation></TranslationSet><TranslationStack>   <TermSet>    <Term>BRCA1[symbol]</Term>    <Field>symbol</Field>    <Count>283</Count>    <Explode>N</Explode>   </TermSet>   <TermSet>    <Term>"Homo sapiens"[Organism]</Term>    <Field>Organism</Field>    <Count>224685</Count>    <Explode>Y</Explode>   </TermSet>   <OP>AND</OP>  </TranslationStack><QueryTranslation>BRCA1[symbol] AND "Homo sapiens"[Organism]</QueryTranslation></eSearchResult>"""

        gene_ids = example.get_gene_ids_from_xml(xml)
        self.assertEqual(len(gene_ids), 1)
        self.assertEqual(gene_ids[0], 672)
        return

    def test_get_gene_ids_from_gene_symbol(self):
        """
        Test that a call for gene symbol BRCA1 returns at least one
        gene ID.
        """
        gene_ids = example.get_gene_ids_from_gene_symbol("Homo sapiens", "BRCA1")
        self.assertTrue(len(gene_ids) > 0)
        return

if __name__ == "__main__":
    unittest.main()
