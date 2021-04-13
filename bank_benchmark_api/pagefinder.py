import pandas as pd
import numpy as np
import requests
import pdfminer.layout
import pdfminer.high_level
import pdfplumber
import pdfminer.pdftypes
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar, LTTextBox
from pdfminer.pdfpage import PDFPage
import json
import re
from urllib.parse import urljoin
from urllib.request import Request, urlopen
from io import StringIO, BytesIO


## defining global regex match patterns for page finder
searchterms = {
    'Demand Deposits': r'[cC]ontas\sde\s[dD]ep[oó]sito.+articulares.+P[áa]g',
    'Housing Credit':
    r"[Oo]pera[çc][õo]es.{,4}[Cc]r[ée]dito.+articulares.+P[áa]g"
}

## Examples of strings to find on pages
# Operações de crédito / Particulares – Pág. 1 /15
# Operações de Crédito / Particulares - Página 1 / 32
# Operações de Crédito / Particulares - Pág. 1 /29
# Operações Crédito-Particulares - Pág.1/2

class PageFinder:
'''Requires the global bank dict to parse through. THere it will access the bp_pdf_url and look for relevant pages.'''

    def __init__(self, bank_dict):
        self.bank_dict = bank_dict

    def page_finder(self, searchterms):
        products = {}
        for k, val in self.bank_dict.items():
            url = val.get('bp_pdf_url')
            remote = urlopen(Request(url)).read()
            memory = BytesIO(remote)

            pdf = pdfplumber.open(memory)
            products[k] = {'Demand Deposits':[],
                          'Housing Credit':[]}
            for page in pdf.pages:
                if re.search(searchterms.get('Demand Deposits'), page.extract_text()):
                    products[k]['Demand Deposits'].append(page.page_number)
                if re.search(searchterms.get('Housing Credit'), page.extract_text()):
                    products[k]['Housing Credit'].append(page.page_number)

        return products
