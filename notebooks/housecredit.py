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
                    'termination':['Cessação da posição contratual', 'cessação', 'rescisão', 'encerramento']}

# def get_prices(pdf,page, dictionary):
#     doc = pdfplumber.open(pdf)
#     if len(page)==1:
#         prod_df=pd.DataFrame(doc.pages[page[0]].extract_table())
#         def find_prices(df):
#             for x in range(df.shape[0]):
#                 for y in range(df.shape[1]):
#                     if 'Euros' in str(df[y][x]):
#                         return y
#         def find_index(df,dictionary):
#             index_col=list()
#             for x in range(df.shape[0]):
#                 for y in range(find_prices(df)):
#                     if str(df[y][x])=='None' or str(df[y][x])=='' or 'Nota' in str(df[y][x]):
#                         pass
#                     else:
#                         words = [word for word in str(df[y][x]).split(' ')]
#                         for word in words:
#                             for key in dictionary.keys():
#                                 for item in dictionary[key]:
#                                     if word in item:
#                                         index_col.append(y)
#         return int(statistics.mode(index_col))

#         def clean_df(df):
#             for x in range(df.shape[0]):
#                 for y in df.columns:
#                     if str(df[y][x])=='' or str(df[y][x])=='None':
#                         df[y][x]=np.nan
#             return df.dropna(axis='columns', how='all').dropna(axis='rows', how='all')
#         prices_col=find_prices(prod_df)
#         index_col=find_index(prod_df, house_credit_com)
#         prices_df=pd.DataFrame()
#         prices_df['Commissions']=prod_df[index_col]
#         prices_df['Prices']=prod_df[prices_col]
#         return clean_df(prices_df)
# def get_pdf(link):
#         remote = urlopen(Request(link)).read()
#         memory = BytesIO(remote)
#         return memory



# def clean_df(df):
#         for x in range(df.shape[0]):
#             for y in df.columns:
#                 if str(df[y][x])=='' or str(df[y][x])=='None':
#                     df[y][x]=np.nan
#         return df.dropna(axis='columns', how='all').dropna(axis='rows', how='all')


class HouseCredit:

    def __init__(self,link,page):
        self.link = link
        self.page_house = page
        self.commisions = house_credit_com

    def is_avaiable(self):
        if self.page_house == None:
            print(f'This main product is not avaiable for the following bank: {self.link}')
        else:
            print('Ready to scrape!')

    def get_pdf(self):
        remote = urlopen(Request(self.link)).read()
        memory = BytesIO(remote)
<<<<<<< HEAD
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
=======
        return memory

    def getting_text(self,file):
        file = pdfplumber.open(self.get_pdf())
        if self.page_house == None:
            print(f'This main product is not avaiable for the following bank: {self.link}')
        else:
            print('Ready to scrape!')
            if len(self.page_house) > 1 :
                joined_text = []
                for el in self.page_house:
                    page = file.pages[el]
                    text = page.extract_text()
                    joined_text.append(text)
                text ='             NEXT          '.join(joined_text)
                text = text.replace('Isento', '0,00')
                text = text.replace('n/a', '0,00')
                text = re.sub('--', str(np.nan), text)
                print('cleaned the text')
                return text
            else:
                page = file.pages[self.page_house[0]]
                text = page.extract_text()
                text = text.replace('Isento', '0,00')
                text = text.replace('n/a', '0,00')
                text = re.sub('--', str(np.nan), text)
                print('cleaned the text')
                return text

    def tokenize(self, text):
        if len(nltk.sent_tokenize(text)) < 15:
            text = text.replace('\n','. ')
            # text = len_sentences(text)
            text = nltk.sent_tokenize(text)
            return text
        text = text.replace('\n',' ')
        # text = len_sentences(text)
        text = nltk.sent_tokenize(text)
        print('we got the sentences')
        return text

    def n_account(self, text,tokenize):
        # accounts = []
        finals = []
        for sentence in tokenize:
            if 'Crédito' in sentence:
                finals.append(sentence)
        return finals

    def names(self,text,tokanize):
        values = self.n_account(text,tokanize)
        if len(values) < 10:
            return values
        words = []
        for account in values:
            for element in account:
                words.append(element.split())
        names = []
        for word in words:
            if word[0] == 'Crédito' and len(word)>1:
                names.append(word)
        finals = []
        for name in names:
            finals.append(' '.join(name[:14]).replace(';','').replace('/d./d',''))
        search = 'Crédito à habitação e outros créditos hipotecário'
        search2 = 'Crédito / Particulares'
        regular = []
        for final in finals:
            if search not in final:
                if search2 not in final:
                    print(f'append {final} to the list of names')
                    regular.append(final)

        return regular

    def output(self):
        file = self.get_pdf()
        text = self.getting_text(file)
        tokenize = self.tokenize(text)
        output = self.names(text, tokenize)
        # doc = get_pdf(url)
        # prices_df = get_prices(doc, page, dictionary)
        # prices_df.reset_index(drop='index', inplace=True)
        return output
>>>>>>> 371fd2522b9d8d1891f4a98ad5f5d2e672a97d00
