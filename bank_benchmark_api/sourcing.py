import pandas as pd
import numpy as np
import requests
from PyPDF2 import PdfFileReader, PdfFileMerger, PdfFileWriter
import PyPDF2
from bs4 import BeautifulSoup
import os
import shutil
from urllib.parse import urljoin
from urllib.request import Request, urlopen
from io import StringIO, BytesIO
import cloudinary.uploader
import json

# load banks file
with open('raw_data/banks.json') as json_file:
    banks = json.load(json_file)

class PdfSourcing:
    def __init__(self, banks=banks):
        self.banks = banks

    def find_price_pages(self, banks=banks, search=['preçário', 'pricelist', 'precario']):    
        search = [x.lower() for x in search]
        for k, v in banks.items():
            url = v.get('url')
            print(f'parsing url: {url}')
            # only look for the pt page
            headers = {'Accept-Language': 'pt-PT'}
            r = requests.get(url, headers=headers)
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
                        v['pricelist_url'] = urljoin(url,url_prices)
                        print(f'added link to banks: {urljoin(url,url_prices)}')
            else:
                print(f'could not reach page: {url}')
        
        ## SAVE BANK.json back to directory
        with open('raw_data/banks.json', 'w') as fp:
            json.dump(banks, fp)
        
        return banks

    def get_pdf_urls(self, banks=banks):
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
                        if '.pdf' in link.get('href'):
                            # some pdf links are absolute links
                            ## tru out r.url
                            pdf = urljoin(val.get('url'),link.get('href'))
                            print(f'found and added pdf: {pdf}')
                            val['pdfs'].append(f'{pdf}')
                else:
                    print(f'could not execute parsing for: {url}')
            
            ## SAVE BANK.json back to directory
            with open('raw_data/banks.json', 'w') as fp:
                json.dump(banks, fp)

            return banks

    def rerun_sourcing(self, banks=banks):
        banks = self.find_price_pages()
        banks = self.get_pdf_urls(banks)
        
        ## SAVE BANK.json back to directory
        with open('raw_data/banks.json', 'w') as fp:
            json.dump(banks, fp)

        return banks