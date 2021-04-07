import pandas as pd
import numpy as np
import pdfplumber
import re
import nltk


com_dict = {'Emissão de Extrato':['Emissão de extrato', 'Extrato Integrado', 'Extrato Mensal'],
           'Fotocópias e 2ªvias':['Fotocópias de segundas vias de talões de depósito',
                                  'Emissão 2ªs Vias de Avisos e Outros Documentos', 'Extracto avulso',
                                 'Segundas vias (pedido na agência)'],
           'Manutenção de Conta':['Manutenção de conta', 'Comissão de manutenção de conta'],
           'Levantamento de Numerário':['Levantamento de numerário', 'Levantamento de numerário ao balcão'],
           'Adesão ao Serviço Online':['Adesão ao serviço de banca à distância', 'Adesão ao serviço online'],
            'Depósitos de Moedas':['Depósito de moedas metálicas', 'Depósito de moedas',
                                   'Depósito de moedas ao balcão', 'Depósito de dinheiro ao balcão',
                                  'Depósito de moeda metálica (≥ a 100 moedas)'],
            'Ateração de Titulares':['Alteração de titulares', 'Alteração de titularidade',
                                     'Alteração de titularidade / intervenientes'],
            'Descoberto Bancário':['Comissões por descoberto bancário', 'Descoberto bancário'],
            'Consulta de Movimentos':['Consulta de Movimentos de conta DO com', 'Consulta de movimentos ao balcão'],
            'Consulta de Saldo':['Pedido de saldo ao balcão', 'Consulta de Saldo de conta DO com comprovativo']
           }






class Scraping:
    def __init__(self, pdf, page, x):
        self.pdf = pdf
        self.page = [page]
        self.x = x


    def getting_text(self):
        file = pdfplumber.open(self.pdf)
        if len([self.page]) > 1 :
            joined_text = []
            for el in self.page:
                page = file.pages[el]
                text = page.extract_text()
                joined_text.append(text)
            text ='             NEXT          '.join(joined_text)
            text = text.replace('Isento', '0,00')
            text = text.replace('n/a', str(np.nan))
            text = re.sub('--', str(np.nan), text)
            return text
        else:
            page = file.pages[[self.page][0]]
            text = page.extract_text()
            text = text.replace('Isento', '0,00')
            text = text.replace('n/a', str(np.nan))
            text = re.sub('--', str(np.nan), text)
            return text

    def tokenize(self):
        text = self.getting_text()
        if len(nltk.sent_tokenize(text)) < 15:
            text = text.replace('\n','. ')
            # text = len_sentences(text)
            text = nltk.sent_tokenize(text)
            return text
        text = text.replace('\n',' ')
        # text = len_sentences(text)
        text = nltk.sent_tokenize(text)
        return text

    # def search_com(self):
    #     decod = {}
    #     if self.x not in commission:
    #         return 'not in the dictionary'
    #     decod = commission[self.x]
    #     file = self.tokenize()
    #     return decod, file

    def values(self):
        file = self.tokenize()
        values = [x for x in com_dict.values()]
        lista ={}
        for commission in values:
            for value in commission:
                for ind,sentence in enumerate(file):
                    if value in sentence:
                        if value in lista:
                            if '[0-9]{1-2},[0-9]{2}' in sentence:
                                lista[value]= lista[value].append(sentence)
                            else:
                                lista[value]= lista[value].append(' '.join([sentence,file[ind+1]]))
                        else:
                            if '[0-9]{1-2},[0-9]{2}' in sentence:
                                lista[value]= [sentence]
                            else:
                                lista[value]= [' '.join([sentence,file[ind+1]])]
        return lista

    def n_account(self):
        accounts = []
        finals = []
        text = self.getting_text()
        if len(nltk.sent_tokenize(text)) < 15 :
            for sentence in self.tokenize():
                if 'Conta' in sentence:
                    finals.append(sentence)
            return finals
        for sentence in self.tokenize():
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
            finals.append(' '.join(name[:14]).replace(';','').replace('/d./d',''))
        regular = []
        for final in finals:
            start = final[:3]
            if start not in regular:
                regular.append(final)
        return regular
