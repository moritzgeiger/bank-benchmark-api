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


bank_dir = 'bank_benchmark_api/data/banks.json'
search_terms = ['preçário', 'pricelist', 'precario']
# # load banks file
# with open('bank_benchmark_api/data/banks.json') as json_file:
#     banks = json.load(json_file)

class PdfSourcing:
    def __init__(self):
        pass

    def find_price_pages(self, bank_dir=bank_dir, search=search_terms):    
        search = [x.lower() for x in search]
        # load banks file
        with open(bank_dir) as json_file:
            banks = json.load(json_file)

        for k, v in banks.items():
            url = v.get('url')
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
                        v['pricelist_url'] = urljoin(url,url_prices)
                        print(f'added link to banks: {urljoin(url,url_prices)}')
            else:
                print(f'could not reach page: {url}')
        
        ## SAVE BANK.json back to directory
        with open(bank_dir, 'w') as fp:
            json.dump(banks, fp)
        
        return banks

    def get_pdf_urls(self, bank_dir=bank_dir):
        # load banks file
        print(f'loading banks from origin {bank_dir}')
        with open(bank_dir) as json_file:
            banks = json.load(json_file)
        
        for val in banks.values():
            url = val.get('pricelist_url')
            val['pdfs'] = list()
            # some banks direclty link to a pdf address
            if '.pdf' in url:
                print(f'url is already pdf for: {url}')
                val['pdfs'].append(f'{url}')
            # for other landing pages look for every pdf on page
            else:
                r = requests.get(url)
    #             print(type(val['pdfs']))
                if r.status_code == 200:
                    soup = BeautifulSoup(r.content, 'html.parser')
                    print(f'looking for pdfs in: {url}')
                    for link in soup.find_all('a', href=True):
                        href = link.get('href')
                        if '.pdf' in href:
                            # some pdf links are absolute links

                            # href = quote_plus(href)
                            pdf = urljoin(val.get('url'),href)
                            val['pdfs'].append(f'{pdf}')
                            print(f'found and added pdf: {pdf}')
                    print(f'final list of pdfs: {val.get("pdfs")}')
                else:
                    print(f'could parse though: {url}')
            
        ## SAVE BANK.json back to directory
        print('saving banks back to origin {bank_dir}') 
        with open(bank_dir, 'w') as fp:
            json.dump(banks, fp)

        return banks

    def rerun_sourcing(self, bank_dir=bank_dir):
        # with open(bank_dir) as json_file:
        #     banks = json.load(json_file)
        banks = self.find_price_pages()
        banks = self.get_pdf_urls()
        
        ## SAVE BANK.json back to directory
        with open(bank_dir, 'w') as fp:
            json.dump(banks, fp)

        return banks