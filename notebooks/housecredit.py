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



def clean_df(df):
        for x in range(df.shape[0]):
            for y in df.columns:
                if str(df[y][x])=='' or str(df[y][x])=='None':
                    df[y][x]=np.nan
        return df.dropna(axis='columns', how='all').dropna(axis='rows', how='all')


class HouseCredit:

    def __init__(self,link,page):
        self.link = link
        self.page = page
        self.word = 'Euros'

    def get_pdf(self):
        remote = urlopen(Request(self.link)).read()
        memory = BytesIO(remote)
        file = pdfplumber.open(memory)
        dataframes = []
        for el in self.page:
                page = file.pages[el]
                table = page.extract_table()
                df = pd.DataFrame(table)
                dataframes.append(df)
        return pd.concat(dataframes, ignore_index=True)


    def find_prices(self):
        df = self.get_pdf()
        for x in range(df.shape[0]):
            for y in range(df.shape[1]):
                if self.word in str(df[y][x]):
                    return y

    def find_index(self):
        index_col=list()
        df = self.get_pdf()
        for x in range(df.shape[0]):
            for y in range(df.shape[1]):
                if df[y][x]=='None':
                    pass
                else:
                    for key in house_credit_com.keys():
                        if df[y][x] in house_credit_com[key]:
                            index_col.append(y)
        return int(statistics.median(index_col))



    def total(self):
        prices_col= self.find_prices()
        index_col= self.find_index()
        prices_df=pd.DataFrame()
        prices_df['Commissions']=self.get_pdf()[index_col]
        prices_df['Prices']=self.get_pdf()[prices_col]
        return clean_df(prices_df)
x
