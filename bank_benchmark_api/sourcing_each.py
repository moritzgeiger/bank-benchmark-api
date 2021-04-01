import pandas as pd
import numpy as np
import requests
from PyPDF2 import PdfFileReader, PdfFileMerger, PdfFileWriter
import PyPDF2
from bs4 import BeautifulSoup
import os
import shutil
from urllib.parse import urljoin, urlencode, quote_plus
from urllib.request import Request, urlopen
# from io import StringIO, BytesIO
import cloudinary.uploader
import json

from bank_benchmark_api.data.bank_details import bp_bank_id

search_terms = ['preçário', 'pricelist', 'precario']
# # load banks file
# with open('bank_benchmark_api/data/banks.json') as json_file:
#     banks = json.load(json_file)


class PdfSourcing:
    def __init__(self, bank_dict):
        self.bank_dict = bank_dict

    def find_price_pages(self, search=search_terms):    
        search = [x.lower() for x in search]

        for bank_id, vals in self.bank_dict.items():
            url = vals.get('url')
            print(f'parsing url: {url}')
            # only look for the pt page
            headers = {'Accept-Language': 'pt-PT'}
            try:
                r = requests.get(url, headers=headers)
            except:
                print(f'coud not reach url: {url}')
                break
            soup = BeautifulSoup(r.content, 'html.parser')
            if r.status_code == 200:
                # going through every link on the page to see if 'precarios' is in the link
                for link in soup.find_all('a', href=True):
                    url_prices = str(link.get('href').lower().strip())
                    lower = str(link.string).lower().strip()
                    title = str(link.get('title')).strip().lower()
                    searchstring = ' '.join([url_prices, lower, title])
                    if any([x in searchstring for x in search]):
                        print(f'found terms of {search} in string {searchstring}')
                        # some links in the source code are relative, some are absolute -- using urljoin
                        #################### FIGURE OUT ENCODING URL!!! ###
                        
                        # url_prices = quote_plus(url_prices)
                        # adding findings to bank dictionary
                        vals["price_page"] = urljoin(url,url_prices)
                        print(f'added link to id {bank_id}: {urljoin(url,url_prices)}')
            else:
                print(f'could not reach page: {url}')

        return self.bank_dict

    ### will only run after find_price_pages!
    def get_bp_pdf_urls(self):

        ## setting url canvas
        url_pre = 'https://clientebancario.bportugal.pt/sites/default/files/precario/'
        url_suff = '_PRE.pdf'
        for bank_id, vals in self.bank_dict.items():
            try:    
                bp_bank_id = vals.get('bp_bank_id')
                vals['bp_pdf_url'] = f'{url_pre}{bp_bank_id}_/{bp_bank_id}{url_suff}'
            except:
                print(f'The id {bank_id} does not have a bp_bank_id. Please update the variable.')
        
        return self.bank_dict

    def get_banks_pdf_urls(self):
   
        for bank_id, vals in self.bank_dict.items():
            price_page = val.get('price_page')
            # creating empty list for pdf urls
            vals['list_pdfs'] = []
            # some banks direclty link to a pdf address
            if '.pdf' in price_page:
                print(f'url is already pdf for: {price_page}')
                vals['list_pdfs'].append(f'{price_page}')
            # for other landing pages look for every pdf on page
            else:
                r = requests.get(price_page)
                if r.status_code == 200:
                    soup = BeautifulSoup(r.content, 'html.parser')
                    print(f'looking for pdfs in: {price_page}')
                    for link in soup.find_all('a', href=True):
                        href = link.get('href')
                        if '.pdf' in href:
                            # some pdf links are absolute links

                            # href = quote_plus(href)
                            pdf = urljoin(val.get('url'),href)
                            vals['list_pdfs'].append(f'{pdf}')
                            print(f'found and added pdf: {pdf}')
                    print(f'final list of pdfs added: {vals.get("list_pdfs")}')
                else:
                    print(f'could parse though: {price_page}')

        return self.bank_dict

    ## todo: nuber of pdfs
    ## todo: nuber of last_updated
    ## todo: nuber of sum_sizes

    def rerun_sourcing(self):
        # with open(bank_dir) as json_file:
        #     banks = json.load(json_file)
        banks = self.get_bp_pdf_urls()
        banks = self.find_price_pages()
        banks = self.get_banks_pdf_urls()

        return banks