import pandas as pd
import numpy as np
import pdfplumber
import re
import nltk


commission = {'abanca': {'1':'Emissão de extrato','2':'Fotocópias de segundas vias de talões de depósito',\
                        '3': 'Manutenção de conta', '4': {'Levantamento de numerário':{'4.1':'Ao balcão, com apresentação de cheque',\
                                                                                      '4.2': 'Ao balcão, sem apresentação de cheque'},\
                                                         }, '5': 'Adesão ao serviço de banca à distância', '6':'Depósito de moedas metálicas',\
                        '7':'Alteração de titulares'}, \
              'ctt':{'1':'Extrato Integrado mensal', '2':'Consulta de Saldo de conta DO com comprovativo',\
                     '3':'Consulta de Movimentos de conta DO com comprovativo', '4': 'Emissão 2as Vias de Avisos e Outros Documentos',\
                     '5':'Alteração de titularidade'},
              'bic':{'1':'Manutenção de conta','2':'Levantamento de numerário','3':'Levantamento USD em contas USD',\
                    '4': 'Extracto integrado','5':'Extracto avulso'}}


def len_sentences(x):
        if len(nltk.sent_tokenize(x))== 1:
            return x.replace('\n','. ')
        return x.replace('\n','')


class Scraping:
    def __init__(self, pdf, page):
        self.pdf = pdf
        self.page = page


    def extract_clean(self):
        file = pdfplumber.open(self.pdf)
        page = file.pages[self.page]
        text = page.extract_text().lower()
        text = re.sub('isento', '0,00', text)
        text = re.sub('n/a', str(np.nan), text)
        text = re.sub('--', str(np.nan), text)
        text=text.replace('\n','')
        text = len_sentences(text)
        text = nltk.sent_tokenize(text)
        return text

    def search_com(self, x):
        decod = {}
        if x not in commission:
            return 'not in the dictionary'
        decod = commission[x]
        file = self.extract_clean()
        return decod, file

