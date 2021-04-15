import pandas as pd
import numpy as np
import pdfplumber
import re
import nltk
from urllib.parse import urljoin, quote_plus, quote, urlencode
from urllib.request import Request, urlopen
from io import StringIO, BytesIO
import statistics

house_credit_com = {'admin':['Comissões associadas a atos administrativos 4.1 Não realização da escritura',
                             'Alteração do local da escritura',
                             'Declarações de dívida',
                             'Mudança de regime de crédito',
                             'Declarações de dívida',
                             'Pedido de 2ª via de Caderneta Predial',
                             'Emissão de declarações não obrigatórias por lei',
                             'Emissão de 2ª vias de Declaração para efeitos de IRS – Urgente',
                             'Emissão de 2º vias de Declaração para efeitos de IRS',
                             'Emissão de 2ª vias de faturas',
                             'Declaração de Dívida para Fins Diversos',
                             'Declaração de Encargos com Prestações'],
                    'certificates':['Emolumentos do registo predial', 'registo predial',
                                    'Certidão permanente on-line'],
                    'debt_recovery':['Comissão de recuperação de valores em dívida', 'Prestação até 50.000 €',
                                    'Prestação > 50.000 €', 'Comissão de recuperação de valores em dívida',
                                    'Prestação > 50.000,00€', 'Prestação ≤ 50.000,00€'],
                    'displacement':['Comissão de deslocação', 'Até 100 Kms', '101 a 250 Kms', '> 250 Kms '],
                    'early_payment':['Comissão de reembolso antecipado parcial', 'Taxa fixa', 'Taxa variável',
                                    'Taxa fixa', 'Comissão de reembolso antecipado total', 'Comissão de antecipação',
                                    '(pré.aviso 7 dias)', 'Comissão de compra antecipada', '(pré-aviso 10 dias)',
                                    'Comissão de Reembolso Antecipado Parcial',
                                    'Comissão de reembolso antecipado total'],
                    'evaluation':['Avaliação', 'Imóvel residencial',
                                 'Garagens e arrecadações não anexas ao imóvel residencial', 'Avaliação do Imóvel'],
                    'formalization':['Comissão de formalização', 'Formalização'],
                    'process':['Processo', 'Abertura de Processo',
                              'Desistência ou não conclusão do processo por motivos imputáveis ao cliente'],
                    'inspections':['Vistorias', 'em caso de construção ou realização de obras'],
                    'reanalysis':['Reanálise'],
                    'settlement':['Comissão de Liquidação de Prestação', 'Liquidação de Prestação'],
                    'solicitors_notary':['Emolumentos notariais', 'Solicitadoria', 'Notiário'],
                    'statements':['Emissão de extratos de conta de empréstimos liquidados', 'extrato', 'extratos',
                                  'extrato de conta', 'extrato mensal'],
                    'taxes':['Imposto do Selo sobre concessão de crédito', 'imposto', 'imposto de selo', 'impostos'],
                    'termination':['Cessação da posição contratual', 'cessação', 'rescisão', 'encerramento']
                    }


def get_df(pdf,page, dictionary):
    doc = pdfplumber.open(pdf)
    prod_df=pd.DataFrame(doc.pages[page].extract_table())

    prices_col=find_prices(prod_df)
    index_col=find_index(prod_df, house_credit_com)

    prices_df=pd.DataFrame()
    prices_df['Commissions']=prod_df[index_col]
    prices_df['Prices']=prod_df[prices_col]

    return clean_df(prices_df)

def find_prices(df):
    col=''
    for x in range(df.shape[0]):
        for y in range(df.shape[1]):
            if 'Euros' in str(df[y][x]):
                col = y
    if col=='':
        col=3
    return col

def find_index(df,dictionary):
    index_col=list()
    for x in range(df.shape[0]):
        for y in range(find_prices(df)):
            if str(df[y][x])=='None' or str(df[y][x])=='' or 'Nota' in str(df[y][x]):
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
            if str(df[y][x])=='' or str(df[y][x])=='None':
                df[y][x]=np.nan
    return df.dropna(axis='columns', how='all').dropna(axis='rows', how='all')


def get_pdf(link):
        remote = urlopen(Request(link)).read()
        memory = BytesIO(remote)
        return memory


def scrape_page(url, page, dictionary):
    doc=get_pdf(url)
    prices_df=get_df(doc, page, dictionary)
    prices_df.reset_index(drop='index', inplace=True)
    return prices_df

def clean_prices(df):
    commissions={}
    for i in range(len(df)):
        if str(df['Prices'][i])=='nan':
            df['Prices'][i]='0'
        else:# re.search(r'\d+,\d{2}/\d+,\d{2}', df['Prices'][i]):
            df['Prices'][i]='&'.join(re.findall(r'\d+,\d{2}', df['Prices'][i]))
        if df['Prices'][i]=='':
            df['Prices'][i]='0'
        if type(df['Commissions'][i])==str:
            if 'Nota' in df['Commissions'][i]:
                pass
            elif '\n-' in df['Commissions'][i]:
                names=df['Commissions'][i].split(sep='\n-')
                prices=['']+df['Prices'][i].split(sep='&')
                names=[n.replace('\n', '') for n in names]
                #prices=[p.replace('','0') for p in prices]
                commissions.update({names[0]:{}})
                commissions[names[0]].update({name: price for name, price in zip(names[1:], prices[1:])})
            elif '\n ' in df['Commissions'][i]:
                names=df['Commissions'][i].split(sep='\n ')
                prices=['']+df['Prices'][i].split(sep='&')
                names=[n.replace('\n', '') for n in names]
                #prices=[p.replace('','0') for p in prices]
                commissions.update({names[0]:{}})
                commissions[names[0]].update({name: price for name, price in zip(names[1:], prices[1:])})
            elif len(re.findall(r'\n[0-9]', df['Commissions'][i]))>0:
                names=re.split(r'\n[0-9]', df['Commissions'][i])
                prices=['']+df['Prices'][i].split(sep='&')
                names=[n.replace('\n', '') for n in names]
                #prices=[p.replace('','0') for p in prices]
                commissions.update({names[0]:{}})
                commissions[names[0]].update({name: price for name, price in zip(names[1:], prices[1:])})
            else:
                name = df['Commissions'][i]
                price = df['Prices'][i]
                if '&' in price:
                    price=df['Prices'][i].split(sep='&')[-1]
                name = name.replace('\n','').replace('\xa0','')
                commissions.update({name: price})
    return commissions

def scrape_all(url, pages, dictionary):
    house_cred={}
    if len(pages)>0:
        for page in pages:
            df=scrape_page(url, page, dictionary)
            house_cred.update({f'page {page}': clean_prices(df)})
        result=house_cred
    else:
        result='No housing credit product found in this bank'
    return result


class HouseCredit:

    # def __init__(self,dictionary):
    #     self.link = dictionary['bp_pdf_url']
    #     self.page_house = dictionary['products']['house_credit']['pages']
    #     self.id_bank = dictionary['bp_bank_id']
    #     self.house_dict = dictionary['products']['house_credit']['commissions']
    def __init__(self,link,page):
        self.link = link
        self.page_house = page
        # self.id_bank = dictionary['bp_bank_id']
        self.house_dict = house_credit_com


#    def total(self):
#        file = get_pdf(self.link)
#        result={}
#        for page in self.page_house:
#            prices_df=get_prices(file, page, self.house_dict)
#            result.update({f'page {page}': clean_prices(prices_df)})
#        final = {}
#        for page in result.values():
#            for k in page.keys():
#        #         print(k)
#                if 'Nota' not in k:
#                    final[k] = page[k]
#        return final

    def scrape_all(self):
        house_cred={}
        if len(self.page_house)>0:
            for page in self.page_house:
                df=scrape_page(self.link, page, self.house_dict)
                house_cred.update({f'page {page}': clean_prices(df)})
            result=house_cred
        else:
            result='No housing credit product found in this bank'
        return result


