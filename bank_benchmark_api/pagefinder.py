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
from urllib.parse import urljoin, urlencode, quote
from urllib.request import Request, urlopen
from io import StringIO, BytesIO


## defining global regex match patterns for page finder

## Examples of strings to find on pages
# Operações de crédito / Particulares – Pág. 1 /15
# Operações de Crédito / Particulares - Página 1 / 32
# Operações de Crédito / Particulares - Pág. 1 /29
# Operações Crédito-Particulares - Pág.1/2

class PageFinder:
    """
    Requires ONE single bank dict to parse through. There it will access the bp_pdf_url and look for relevant pages via regex.
    returns the enriched dict of the single bank"""

    def __init__(self, single_bank):
        self.single_bank = single_bank

    def find_page(self):
        ## opening the bp file
        print('find_page was called')
        url = self.single_bank.get('bp_pdf_url')
        print(f'opening {url}')
        remote = urlopen(Request(url)).read()
        memory = BytesIO(remote)
        pdf = pdfplumber.open(memory)
        # looking for the products
        products = self.single_bank.get('products')
        # initializing 'pages' list inside products
        print(f'dealing with: {products}')
        for product, val in products.items():
            val['pages'] = []
        # avoiding loading time => looking for all product terms on each page instead of one product per loop
        pt_terms = {key:val.get('portuguese').lower() for (key, val) in products.items()}
        pt_terms_re = {key:re.sub('[^a-zA-Z0-9 \n\.]|\sde\s', '.{,5}', val)+'.{,5}particulares.{,5}p[áa]g' for (key,val) in pt_terms.items()}

        for page in pdf.pages:
            text = page.extract_text().lower()
            for product, term in pt_terms_re.items():
                if re.search(term, text):
                    pagenr = int(page.page_number) -1
                    print(f'found related terms on page {pagenr} for {product}')
                    products[product]['pages'].append(pagenr)
            print(f'continue search in page: {page.page_number}')

        # injecting the updated/enriched products dict in the products
        self.single_bank['products'] = products

        return self.single_bank
