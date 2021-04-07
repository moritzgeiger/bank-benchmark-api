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
              'bai':{'1':'Manutenção de conta','2':'Levantamento de numerário','3':'Levantamento usd em contas usd',\
                    '4': 'Extracto integrado','5':'Extracto avulso'},
             'bankinter':{'1':'Comissão de Manutenção de Conta', '2': 'Comissão de Alteração de Titularidade',
                          '3':'Comissão de Levantamento'},
             'bic': {'1':'Comissão de manutenção de conta','2':'Segundas vias (pedido na agência)','3':'Levantamento de numerário',
                    '4': 'Pedido de saldo ao balcão', '5':'Descoberto bancário', '6':'Depósito de moeda metálica',
                    '7':'Alteração de titularidade'}}




class Scraping:
    def __init__(self, pdf, page, x, splitting_right=False):
        self.pdf = pdf
        self.page = page
        self.x = x
        self.splitting_right = splitting_right

    def extract_clean(self):
        file = pdfplumber.open(self.pdf)
        if len(self.page) > 1 :
            joined_text = []
            for el in self.page:
                page = file.pages[el]
                text = page.extract_text()
                joined_text.append(text)
            text ='             NEXT          '.join(joined_text)
            text = text.replace('Isento', '0,00')
            text = text.replace('n/a', str(np.nan))
            text = re.sub('--', str(np.nan), text)
            if nltk.sent_tokenize(text):
                if self.splitting_right == True:
                    text = text.replace('\n','. ')
                    # text = len_sentences(text)
                    text = nltk.sent_tokenize(text)
                    return text
                text = text.replace('\n',' ')
                # text = len_sentences(text)
                text = nltk.sent_tokenize(text)
            return text
        else:
            page = file.pages[self.page[0]]
            text = page.extract_text()
            text = text.replace('Isento', '0,00')
            text = text.replace('n/a', str(np.nan))
            text = re.sub('--', str(np.nan), text)
            if nltk.sent_tokenize(text):
                if self.splitting_right == True:
                    text = text.replace('\n','. ')
                    # text = len_sentences(text)
                    text = nltk.sent_tokenize(text)
                    return text
                text = text.replace('\n',' ')
                # text = len_sentences(text)
                text = nltk.sent_tokenize(text)
            return text

    def search_com(self):
        decod = {}
        if self.x not in commission:
            return 'not in the dictionary'
        decod = commission[self.x]
        file = self.extract_clean()
        return decod, file

    def values(self):
        file = self.search_com()[1]
        names = self.search_com()[0]
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

    def n_account(self):
        accounts = []
        finals = []
        if self.splitting_right == True:
            for sentence in self.search_com()[1]:
                if 'Conta' in sentence:
                    finals.append(sentence)
            return finals
        for sentence in self.search_com()[1]:
            contas = re.split('Conta',sentence)
            accounts.append(contas)
        for account in accounts:
            if len(account)>1:
                account = ['Conta'+ x for x in account]
                finals.append(account)
        return finals

    def names(self):
        words = []
        for account in self.n_account():
            for element in account:
                words.append(element.split())
        names = []
        for word in words:
            if word[0] == 'Conta' and len(word)>1 and word[1]!='nan':
                names.append(word)
        finals = []
        for name in names:
            finals.append(' '.join(name[:14]).replace(';',''))
        regular = []
        for final in finals:
            start = final[:3]
            if start not in regular:
                regular.append(final)
        return regular


