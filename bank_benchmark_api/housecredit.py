import pandas as pd
import numpy as np
import pdfplumber
import re
import nltk
import requests
from urllib.parse import urljoin, quote_plus, quote, urlencode
from urllib.request import Request, urlopen
from io import StringIO, BytesIO
import statistics


def get_df(pdf, page, dictionary):
    doc = pdfplumber.open(pdf)
    prod_df = pd.DataFrame(doc.pages[page].extract_table())

    prices_col = find_prices(prod_df)
    index_col = find_index(prod_df, dictionary)

    prices_df = pd.DataFrame()
    prices_df['Commissions'] = prod_df[index_col]
    prices_df['Prices'] = prod_df[prices_col]

    return clean_df(prices_df)


def find_prices(df):
    col = ''
    for x in range(df.shape[0]):
        for y in range(df.shape[1]):
            if 'Euros' in str(df[y][x]):
                col = y
    if col == '':
        col = 3
    return col


def find_index(df, dictionary):
    index_col = list()
    for x in range(df.shape[0]):
        for y in range(find_prices(df)):
            try:
                if str(df[y][x]) == 'None' or str(
                        df[y][x]) == '' or 'Nota' in str(df[y][x]):
                    pass
            except:
                pass
            else:
                words = [word for word in str(df[y][x]).split(' ')]
                for word in words:
                    for key in dictionary.keys():
                        for item in dictionary[key]:
                            if word in item:
                                index_col.append(y)
    return int(statistics.mode(index_col))


def clean_df(df):
    for x in range(df.shape[0]):
        for y in df.columns:
            if str(df[y][x]) == '' or str(df[y][x]) == 'None':
                df[y][x] = np.nan
    return df.dropna(axis='columns', how='all').dropna(axis='rows', how='all')


def get_pdf(link):
    remote = urlopen(Request(link)).read()
    memory = BytesIO(remote)
    return memory


def scrape_page(url, page, dictionary):
    doc = get_pdf(url)
    prices_df = get_df(doc, page, dictionary)
    prices_df.reset_index(drop='index', inplace=True)
    return prices_df


def clean_prices(df):
    commissions = {}
    for i in range(len(df)):
        if str(df['Prices'][i]) == 'nan':
            df['Prices'][i] = '0'
        else:  # re.search(r'\d+,\d{2}/\d+,\d{2}', df['Prices'][i]):
            df['Prices'][i] = '&'.join(
                re.findall(r'\d+,\d{2}', df['Prices'][i]))
        if df['Prices'][i] == '':
            df['Prices'][i] = '0'
        if type(df['Commissions'][i]) == str:
            if 'Nota' in df['Commissions'][i]:
                pass
            elif '\n-' in df['Commissions'][i]:
                names = df['Commissions'][i].split(sep='\n-')
                prices = [''] + df['Prices'][i].split(sep='&')
                names = [n.replace('\n', '') for n in names]
                #prices=[p.replace('','0') for p in prices]
                commissions.update({names[0]: {}})
                commissions[names[0]].update({
                    name: price
                    for name, price in zip(names[1:], prices[1:])
                })
            elif '\n ' in df['Commissions'][i]:
                names = df['Commissions'][i].split(sep='\n ')
                prices = [''] + df['Prices'][i].split(sep='&')
                names = [n.replace('\n', '') for n in names]
                #prices=[p.replace('','0') for p in prices]
                commissions.update({names[0]: {}})
                commissions[names[0]].update({
                    name: price
                    for name, price in zip(names[1:], prices[1:])
                })
            elif len(re.findall(r'\n[0-9]', df['Commissions'][i])) > 0:
                names = re.split(r'\n[0-9]', df['Commissions'][i])
                prices = [''] + df['Prices'][i].split(sep='&')
                names = [n.replace('\n', '') for n in names]
                #prices=[p.replace('','0') for p in prices]
                commissions.update({names[0]: {}})
                commissions[names[0]].update({
                    name: price
                    for name, price in zip(names[1:], prices[1:])
                })
            else:
                name = df['Commissions'][i]
                price = df['Prices'][i]
                if '&' in price:
                    price = df['Prices'][i].split(sep='&')[-1]
                name = name.replace('\n', '').replace('\xa0', '')
                commissions.update({name: price})
    return commissions


def scrape_all(url, pages, dictionary):
    house_cred = {}
    if len(pages) > 0:
        for page in pages:
            df = scrape_page(url, page, dictionary)
            house_cred.update({f'page {page}': clean_prices(df)})
        result = house_cred
    else:
        result = {'error': 'No housing credit product found in this bank'}
    return result


class HouseCredit:
    def __init__(self, dictionary):
        self.link = dictionary['bp_pdf_url']
        self.page_house = dictionary['products']['housing_credit']['pages']
        self.page_house = [int(x) for x in self.page_house]
        self.id_bank = dictionary['bp_bank_id']
        self.house_dict = dictionary['products']['housing_credit'][
            'commissions']

    # def __init__( self,link,page, id_bank):
    #     self.link = link
    #     self.page_house = page
    #     self.id_bank = id_bank
    #     self.house_dict = house_credit_com
    def get_pdf(self):
        print(f'opening url: {self.link}...')
        remote = urlopen(Request(self.link)).read()
        memory = BytesIO(remote)
        return memory

    def getting_text(self, file):
        file = pdfplumber.open(file)
        print('extract pdf content to text...')
        if len(self.page_house) > 1:
            joined_text = []
            for el in self.page_house:
                page = file.pages[el]
                text = page.extract_text()
                joined_text.append(text)
            text = '             NEXT          '.join(joined_text)
            text = text.replace('Isento', '0,00')
            text = text.replace('n/a', '0,00')
            text = re.sub('--', str(np.nan), text)
            return text
        ### no pages provided for banco bai
        elif len(self.page_house) == 0:
            return 'No product here'
        else:
            page = file.pages[self.page_house[0]]
            text = page.extract_text()
            text = text.replace('Isento', '0,00')
            text = text.replace('n/a', '0,00')
            text = re.sub('--', str(np.nan), text)
            return text

    def tokenize(self, text):
        print('tokenize text...')
        if len(nltk.sent_tokenize(text)) < 15:
            text = text.replace('\n', '. ')
            # text = len_sentences(text)
            text = nltk.sent_tokenize(text)
            return text
        text = text.replace('\n', ' ')
        # text = len_sentences(text)
        text = nltk.sent_tokenize(text)
        return text

    def n_account(self, text, tokenized):
        finals = []
        for sentence in tokenized:
            if 'Cr??dito' in sentence or 'Habita????o' in sentence:
                finals.append(sentence)
        return finals

    def names(self, text, tokenized):
        values = self.n_account(text, tokenized)
        print(f'found these headers in parsed pages: {values}')
        regular = []
        if self.id_bank == '0170':  #or self.id_bank== '0193':
            for value in values:
                if 'OPERA????ES DE CR??DITO (PARTICULARES)' in value:
                    regular.append(
                        value.replace('OPERA????ES DE CR??DITO (PARTICULARES)',
                                      ''))

        elif self.id_bank == '0193':
            for value in values:
                if 'Banco CTT, S.A. Opera????es Cr??dito-Particulares - P??g.1/2' not in value:
                    regular.append(value)

        elif self.id_bank == '0079':
            for value in values:
                product = 'M??tuo a obras e constru????es (Fora de comercializa????o)'
                search = 'Comiss??o'
                search2 = 'Cr??dito / Particulares'
                search3 = 'Aplic??vel'
                search4 = 'Nota 1 Cr??ditoHabita????o'
                search5 = 'Incluem-se'
                value = value.replace(
                    'Cr??dito ?? habita????o e outros cr??ditos hipotec??rios (cont.)',
                    '')
                value = value.replace(
                    'Cr??dito ?? habita????o e outros cr??ditos hipotec??rios', '')
                value = value.replace('(cont.)', '')
                value = value.replace(
                    'Comiss??es Acresce Outras Euros Valor Em % Imposto condi????es (M??n/M??x) Anual',
                    '')
                value = value.replace('Outros Cr??ditos Hipotec??rios', '')
                if search not in value and search2 not in value and search3 not in value and search4 not in value and search5 not in value:
                    if len(value) > 5:
                        regular.append(value)
                        regular += [product]
        elif self.id_bank == '0269':
            for i, sentence in enumerate(values):
                if 'Cr??dito ?? habita????o e outros cr??ditos hipotec??rios' in sentence:
                    regular.append(' '.join([sentence, values[i + 1]]))
            # for i,reg in enumerate(regular):
            # print(f'\n\n\n\n\n\n\n\n name {i} : {reg} \n\n\n\n\n\n\n\n')
        return regular

    def n_subproducts(self, text, tokenize):
        return len(self.names(text, tokenize))

    # def scrape_all(self):
    #     house_cred={}
    #     if len(self.page_house)>0:
    #         for page in self.page_house:
    #             df=scrape_page(self.link, page, self.house_dict)
    #             house_cred.update({f'page {page}': clean_prices(df)})
    #         result=house_cred
    #     else:
    #         result = {'error':'No housing credit product found in this bank'}
    #     return result
    def association(self, tokenized, text):
        new_dict = {}
        function = scrape_all(self.link, self.page_house, self.house_dict)
        print(
            f"/////////////// SCRAPE ALL /////////////////////\n {function} \n ///////////////////// END SCRAPE ALL /////////////////"
        )
        names = self.names(text, tokenized)
        print(f'assigning names to the scraped dictionary.')
        print(f'\n\n\n\n\n\n\n\n{len(function.values())}')
        if len(function.values()) > 1:
            for name in names:
                for i, v in enumerate(function.values()):
                    # new_dict[name] = ''
                    name = names[i]
                    name = re.sub(r'\s+', ' ', name)
                    print(f'name : {name}')
                    #print(f'##################### {name} ####################')
                    new_dict[name] = v
            # for i, v in enumerate(function.values()):
            #     # new_dict[name] = ''
            #     name = names[i]
            #     name = re.sub(r'\s+', ' ', name)
            #     print(f'name : {name}')
            #     new_dict[name] = v
        else:
            print(f'no names provided in: {names}')
            new_dict['n/a'] = list(function.values())

        return new_dict

    def output(self):
        print('output was called')
        file = self.get_pdf()
        text = self.getting_text(file)
        tokenized = self.tokenize(text)
        output = {}
        output['subproducts'] = self.association(tokenized, text)
        output['n_subproducts'] = self.n_subproducts(tokenized, text)
        print(f'final output ito be injected: {output}')
        return output
