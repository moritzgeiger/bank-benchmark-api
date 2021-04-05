import pandas as pd
import numpy as np
import pdfplumber
import re
import nltk


commission = {'abanca': {'1':'Emissão de extrato','2':'Fotocópias de segundas vias de talões de depósito',\
                        '3': 'Manutenção de conta', '4': 'Levantamento de numerário', '5': 'Adesão ao serviço de banca à distância', '6':'Depósito de moedas metálicas',\
                        '7':'Alteração de titulares'}, \
              'ctt':{'1':'Extrato Integrado', '2':'Emissão 2ªs Vias de Avisos e Outros Documentos',\
                     '3':'Comissão de manutenção de conta','4':'Levantamento de Numerário ao Balcão',
                     '5':'Comissões por descoberto bancário','6':'Consulta de Movimentos de conta DO com', '7': 'Consulta de Saldo de conta DO com comprovativo',\
                     '8':'Alteração de titularidade'},
              'bic':{'1':'Manutenção de conta','2':'Levantamento de numerário','3':'Levantamento usd em contas usd',\
                    '4': 'Extracto integrado','5':'Extracto avulso'}}





class Scraping:
    def __init__(self, pdf, page):
        self.pdf = pdf
        self.page = page


    def extract_clean(self,splitting_right=False):
        file = pdfplumber.open(self.pdf)
        page = file.pages[self.page]
        text = page.extract_text()
        text = text.replace('Isento', '0,00')
        text = text.replace('n/a', str(np.nan))
        text = re.sub('--', str(np.nan), text)
        if splitting_right == True:
            text = text.replace('\n','. ')
            # text = len_sentences(text)
            text = nltk.sent_tokenize(text)
            return text
        text = text.replace('\n',' ')
        # text = len_sentences(text)
        text = nltk.sent_tokenize(text)
        return text

    def search_com(self, x, splitting_right=False):
        decod = {}
        if x not in commission:
            return 'not in the dictionary'
        decod = commission[x]
        file = self.extract_clean()
        return decod, file

    def values(self,x):
        file = self.search_com(x)[1]
        names = self.search_com(x)[0]
        lista = {}
        keys = [x for x in names.keys()]
        for key in keys:
                for ind,sentence in enumerate(file):
                    if names[key] in sentence:
                        if key in lista:
                            if '[0-9]{1-2},[0-9]{2}' in sentence:
                                lista[names[key]]= lista[key].append(sentence)
                            else:
                                lista[names[key]]= lista[key].append(' '.join([sentence,file[ind+1]]))
                        else:
                            if '[0-9]{1-2},[0-9]{2}' in sentence:
                                lista[names[key]]= [sentence]
                            else:
                                lista[names[key]]= [' '.join([sentence,file[ind+1]])]
        return lista


