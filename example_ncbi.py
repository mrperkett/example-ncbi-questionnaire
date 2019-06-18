#! /usr/bin/env python3
"""
An example script demonstrating:
    - how to use the questionnaire module to collect user input
    - simple memoization (see limit_calls decorator)
    - calling NCBI's eutils from Python and parsing the results

The script prompts the user to select gene symbols to convert to gene IDs using
NCBI's eutils for user selected organisms.
"""

import time

import lxml.etree
import questionnaire
import requests


class limit_calls_basic():
    """
    A basic decorator that limits the time between function calls, but doesn't allow
    for the user to provide the time between calls as an argument
    """

    def __init__(self, func):
        self.func = func
        self.previous_time = None
        self.delta_time = 0.35
        self.small_delta_time = 0.01
        return
    
    def __call__(self, *args):
        # if necessary, sleep before next call
        if self.previous_time is not None:
            time_to_sleep = max(0.0, self.delta_time + self.small_delta_time - (time.time() - self.previous_time))
            if time_to_sleep > 0.0:
                time.sleep(time_to_sleep)

        # make call to func and adjust previous_time accordingly
        val = self.func(*args)
        self.previous_time = time.time()

        return val


class limit_calls():
    """
    A decorator that limits the time between function calls.
    """

    def __init__(self, delta_time=0.35):
        self.previous_time = None
        self.delta_time = delta_time
        self.small_delta_time = 0.01
        return
    
    def __call__(self, func):
        def wrap(*args):
            # if necessary, sleep before next call
            if self.previous_time is not None:
                time_to_sleep = max(0.0, self.delta_time + self.small_delta_time - (time.time() - self.previous_time))
                if time_to_sleep > 0.0:
                    time.sleep(time_to_sleep)
         
            # make call to func and adjust previous_time accordingly
            val = func(*args)
            self.previous_time = time.time()
         
            return val

        return wrap
            

def get_gene_ids_from_xml(xml):
    """
    Extract gene IDs from an xml string returned from NCBI's esearch.

    Args:
        xml (str):

    Return:
        gene_ids (list<int>)
    """
    # Example:
    #
    # <eSearchResult>
    #   <Count>1</Count>
    #   <RetMax>1</RetMax>
    #   <RetStart>0</RetStart>
    #   <IdList>
    #     <Id>672</Id>
    #   </IdList>
    #        .
    #        .
    root = lxml.etree.fromstring(str.encode(xml))
    for node in root:
        if node.tag != "IdList":
            continue

        if len(node) == 0 or node[0].tag != "Id":
            return []

        gene_ids = []
        for sub_node in node:
            try:
                gene_ids.append(int(sub_node.text))
            except:
                pass

        if len(gene_ids) > 0:
            return gene_ids
        else:
            return []

    return []


# NOTE: API limits requests to three/second (per IP address or API key)
# https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/
@limit_calls(delta_time=0.35)
def get_gene_ids_from_gene_symbol(organism, gene_symbol):
    """
    Use NCBI's eutils to convert a gene symbol into gene ID(s).

    Args:
        organism (str): NCBI recognized organism string (Ex: "Homo sapiens", "Mus musculus")
        gene_symbol (str): gene symbol (Ex: "BRCA1")

    Return:
        
    """
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gene&term={gene_symbol}[symbol]+AND+{organism}[organism]"
    response = requests.get(url)

    if not response.ok:
        raise ValueError(f"Invalid ({organism}) or gene symbol ({gene_symbol})")

    gene_ids = get_gene_ids_from_xml(response.text)

    return gene_ids




def get_questionnaire_answers(q):
    """
    """
    selected_organisms = q.answers["organisms"]
    if q.answers["gene_symbol_input"] == "predefined":
        selected_gene_symbols = q.answers["gene_symbols"]
    else:
        # Ex: "BRCA1, BRCA2"
        #       "BRCA1,BRCA2"
        #       "BRCA1 BRCA2"
        text = q.answers["gene_symbols"]
        split_text = text.split()

        selected_gene_symbols = []
        for val in split_text:
            for split_val in val.split(","):
                gene_symbol = split_val.strip()
                if gene_symbol != "":
                    selected_gene_symbols.append(gene_symbol)

    return selected_organisms, selected_gene_symbols


def print_gene_info(organisms, gene_symbols, column_width=20):
    """
    For each of the selected gene symbols and organisms, print the conversion to gene ID.

    Args:
        organisms (list<str>)
        gene_symbols (list<str>)
        column_width (int): left-justified width of organism column

    Return:
        None
    """
    for gene_symbol in gene_symbols:
        print(f"Gene Symbol: {gene_symbol}")

        for organism in organisms:
            # NOTE: you can change the time between calls in this function's decorator
            gene_ids = get_gene_ids_from_gene_symbol(organism, gene_symbol)

            if len(gene_ids) is 0:
                gene_ids_str = ""
            elif len(gene_ids) == 1:
                gene_ids_str = str(gene_ids[0])
            else:
                gene_ids_str = ", ".join(map(str, gene_ids))

            print(f"\t{organism.ljust(column_width)} --> {gene_ids_str}")

    return


def build_questionnaire(predefined_organisms, predefined_gene_symbols):
    """
    Build a questionnaire collecting gene symbols toconvert to gene IDs and the
    organisms for which to do the conversion.

    Args:
        predefined_organisms (list<str>)
        predefined_gene_symbols (list<str>)

    Return:
        questionnaire
    """
    q = questionnaire.Questionnaire()
    q.many("organisms", *predefined_organisms, default="Homo sapiens")
    q.one("gene_symbol_input", "predefined", "user-defined")

    q.many("gene_symbols", *predefined_gene_symbols).condition(("gene_symbol_input", "predefined"))


    def not_blank(value):
        return "enter gene symbol(s)" if not value else None

    q.raw("gene_symbols", 
            prompt="Enter gene symbols separated by white space and/or commas").validate(not_blank).condition(("gene_symbol_input", "user-defined"))

    return q


def main():
    """
    """
    predefined_organisms = ["Homo sapiens", 
                "Mus musculus",
                "Danio rerio",
                "Cricetulus griseus",
                "Bos taurus",
                "Gallus gallus",
                "Sus scrofa",
                "Rattus norvegicus"]
    predefined_gene_symbols = ["BRCA1", "BRCA2", "BAD", "TP63"]

    # build questionnaire
    q = build_questionnaire(predefined_organisms, predefined_gene_symbols)

    # run questionnaire and get answers
    q.run()
    selected_organisms, selected_gene_symbols = get_questionnaire_answers(q)

    # print gene information
    # NOTE: a more useful form of this function would return a pandas dataframe (or
    #           similar), so that the output could be written to csv or xlsx
    width = min(50, max([len(organism) for organism in predefined_organisms]))
    print_gene_info(selected_organisms, selected_gene_symbols, column_width=width)


    return


if __name__ == "__main__":
    main()


