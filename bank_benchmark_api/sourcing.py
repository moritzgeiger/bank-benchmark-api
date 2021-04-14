import pandas as pd
import numpy as np
import requests
from PyPDF2 import PdfFileReader, PdfFileMerger, PdfFileWriter
import PyPDF2
from bs4 import BeautifulSoup
import os
import shutil
from urllib.parse import urljoin, urlencode, quote
from urllib.request import Request, urlopen
from io import StringIO, BytesIO
import json
from datetime import date
import sys
from selenium import webdriver
from seleniumrequests import Firefox, PhantomJS
import time
import ssl



## set the global search terms to look for on a banks website. don't choose to many words as it might catch other / irelevant links.
search_terms = ['preçário', 'pricelist', 'precario']

class PdfSourcing:
    def __init__(self, bank_dict):
        self.bank_dict = bank_dict

    def find_price_pages(self, search=search_terms):
        print('find_price_pages was called')
        search = [x.lower() for x in search]

        for bank_id, vals in self.bank_dict.items():
            url = vals.get('url')
            print(f'parsing url: {url}')
            # only look for the pt page
            headers = {'Accept-Language': 'pt-PT'}
            vals["price_page"] = ''
            try:
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
                            # some links in the source code are relative, some are absolute -- using urljoin - Possible errors: special chars in URL
                            # adding findings to bank dictionary
                            vals["price_page"] = quote(urljoin(url, url_prices),
                                                      safe=(":/?"))
                            print(
                                f'added link to id {bank_id}: {quote(urljoin(url,url_prices), safe=(":/?"))}'
                            )
                else:
                    raise Exception(f'could not reach page: {url}, status code: {r.status_code}')

            except requests.exceptions.SSLError:
                ## banco bai is too fine to let me on their page, therefore I need selenium
                print(f'coud not reach url with requests: {url}\n trying Selenium now...')
                driver = webdriver.Firefox()
                driver.implicitly_wait(20)
                driver.get(url)
                time.sleep(15)
                body = driver.page_source
                soup = BeautifulSoup(driver.page_source,  features="lxml")
                for link in soup.find_all('a', href=True):
                    url_prices = str(link.get('href').lower().strip())
                    lower = str(link.string).lower().strip()
                    title = str(link.get('title')).strip().lower()
                    searchstring = ' '.join([url_prices, lower, title])
                    if any([x in searchstring for x in search]):
                        print(
                            f'found terms of {search} in string {searchstring}'
                        )
                        # some links in the source code are relative, some are absolute -- using urljoin - Possible errors: special chars in URL
                        # adding findings to bank dictionary
                        vals["price_page"] = quote(urljoin(url, url_prices),
                                                   safe=(":/?"))
                        print(
                            f'added link to id {bank_id} with Selenium: {quote(urljoin(url,url_prices), safe=(":/?"))}'
                        )
                if vals["price_page"] == '':
                    print(f'SeleniumTimeout could not find any matching links on page')
                    vals["price_page"] = {
                        'error': f'provided url not reachable: {url}, error: '
                    }
                    continue

        return self.bank_dict

    ### will only run after find_price_pages!
    def get_bp_pdf_urls(self):
        print(f'building links for BP website')
        ## setting url canvas -> the bp files follow a strict structure -- see bp_url
        url_pre = 'https://clientebancario.bportugal.pt/sites/default/files/precario/'
        url_suff = '_PRE'
        url_file_ext = '.pdf'
        for bank_id, vals in self.bank_dict.items():
            bp_bank_id = vals.get('bp_bank_id')
            bp_url = f'{url_pre}{bp_bank_id}_/{bp_bank_id}{url_suff}{url_file_ext}'
            r = requests.get(bp_url)
            if r.status_code == 200:
                vals['bp_pdf_url'] = bp_url
                print(f'found correct link: {bp_url}')
            else:
                # some files of bp follow a slightly different structure with _PRE_0.pdf or _PRE_1.pdf as suffixes
                print(f'Could not find file on {bp_url}. \ntrying other links.')
                for i in range(10):
                    bp_url = f'{url_pre}{bp_bank_id}_/{bp_bank_id}{url_suff}_{i}{url_file_ext}'
                    print(f'trying {bp_url}')
                    r = requests.get(bp_url)
                    if r.status_code == 200:
                        print(f'found correct link: {bp_url}')
                        vals['bp_pdf_url'] = bp_url
                        break
                else:
                    ### what happens if the loop goes all the way through
                    print(f'Could not find file on {bp_url}. \nno bp_pdf_url provided for id: {bank_id}.')
                    vals['bp_pdf_url'] = {
                        'error': f'no valid bp_pdf_url provided for id: {bank_id}.'
                    }

        return self.bank_dict

    def get_banks_pdf_urls(self):
        print(f'building list of pdfs on price pages')
        for bank_id, vals in self.bank_dict.items():
            price_page = vals.get('price_page')
            # creating empty list for pdf urls
            vals['list_pdfs'] = {'urls':[]}
            # some banks block automated scraping
            if 'error' in price_page:
                print(f'could not use {vals.get("url")}')
                break
            # some banks direclty link to a pdf address
            elif '.pdf' in price_page:
                print(f'url is already pdf for: {price_page}')
                vals['list_pdfs']['urls'].append(f'{price_page}')
            # for other landing pages look for every pdf on page
            else:
                try:
                    r = requests.get(price_page)
                    if r.status_code == 200:
                        soup = BeautifulSoup(r.content, 'html.parser')
                        print(f'looking for pdfs in: {price_page}')
                        for link in soup.find_all('a', href=True):
                            href = link.get('href')
                            if any([x in href for x in ['.pdf', '.ashx']]):
                                # some pdf links are absolute links, some relative
                                pdf = quote(urljoin(vals.get('url'), href), safe = (":/?"))
                                vals['list_pdfs']['urls'].append(f'{pdf}')
                                print(f'found and added pdf: {pdf}')
                        print(f'final list of pdfs added: {vals.get("list_pdfs")}')
                    else:
                        raise Exception(f'could not reach page: {price_page}, status code: {r.status_code}')

                except Exception as e:
                    print(
                        f'coud not reach url with requests: {price_page}\n trying Selenium now...'
                    )
                    driver = webdriver.Firefox()
                    driver.implicitly_wait(20)
                    driver.get(price_page)
                    time.sleep(15)
                    body = driver.page_source
                    soup = BeautifulSoup(driver.page_source, features="lxml")
                    print(f'looking for pdfs with selenium in: {price_page}')
                    for link in soup.find_all('a', href=True):
                        href = link.get('href')
                        # some weirdos provide .ashx files not direct .pdfs
                        if any([x in href for x in ['.pdf', '.ashx']]):
                            # some pdf links are absolute links, some relative
                            pdf = quote(urljoin(vals.get('url'), href), safe = (":/?"))
                            vals['list_pdfs']['urls'].append(f'{pdf}')
                            print(f'found and added pdf: {pdf}')

                    print(f'final list of pdfs added: {vals.get("list_pdfs")}')

            if vals['list_pdfs']['urls'] == []:
                print(
                    f'SeleniumTimeout could not find any matching pdfs on {price_page}'
                )
                vals['list_pdfs']['urls'] = {
                    'error':
                    f'no pdfs on page available: {price_page}'
                }
                continue

        return self.bank_dict

    def get_num_pdfs(self):
        for bank_id, vals in self.bank_dict.items():
            len_list = len(vals.get("list_pdfs").get('urls'))
            vals["num_pdfs"] = len_list

        return self.bank_dict


    def last_updated(self):
        for bank_id, vals in self.bank_dict.items():
            vals["last_updated"] = str(date.today())
            vals["status"] = "ok"
        return self.bank_dict


    def sum_sizes(self):
        for bank_id, vals in self.bank_dict.items():
            print(f"checking filesizes of pdfs for {vals.get('price_page')}")
            pdfs = vals.get('list_pdfs')
            if pdfs == []:
                print(f"no pdfs provided for {vals.get('price_page')}")
                break
            else:
                filesizes = []
                for pdf in pdfs:
                    try:
                        remote = urlopen(Request(pdf)).read()
                        memory = BytesIO(remote)
                        # file = PdfFileReader(memory)
                        filesizes.append(sys.getsizeof(memory))
                    except Exception as e:
                        print(f'cannot reach: {pdf}, error: {e}')

                vals['sum_sizes'] = sum(filesizes)
                print(f'filesizes added to {vals.get("url")}')

        return self.bank_dict

    def rerun_sourcing(self):

        banks = self.get_bp_pdf_urls()
        banks = self.find_price_pages()
        banks = self.get_banks_pdf_urls()
        banks = self.get_num_pdfs()
        banks = self.last_updated()
        # banks = self.sum_sizes()

        return banks
