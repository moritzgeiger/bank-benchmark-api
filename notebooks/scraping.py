import pandas as pd
import numpy as np
import pdfplumber
import re
import nltk
from urllib.parse import urljoin, quote_plus, quote, urlencode
from urllib.request import Request, urlopen
from io import StringIO, BytesIO


com_dict = {'statement':['Emissão de extrato', 'Extrato Integrado', 'Extrato Mensal', 'Extrato integrado', 'Extrato avulso'],
           'documents_copy':['Fotocópias de segundas vias de talões de depósito',
                                  'Emissão 2ªs Vias de Avisos e Outros Documentos', 'Extracto avulso',
                                 'Segundas vias (pedido na agência)'],
           'acc_manteinance':['Manutenção de conta', 'Comissão de manutenção de conta', 'Comissão de Manutenção de Conta',
                                'Manutenção de Conta Pacote', 'Manutenção de Conta Base', 'Manutenção de Conta Serviços Mínimos Bancários'],
           'withdraw':['Levantamento de numerário', 'Levantamento de numerário ao balcão', 'Comissão de Levantamento',
                      'Levantamento de Numerário ao Balcão', 'Levantamento de Numerário ao Balcão'],
           'online_service':['Adesão ao serviço de banca à distância', 'Adesão ao serviço online'],
            'cash_deposit':['Depósito de moedas metálicas', 'Depósito de moedas', ' Depósito em moeda metálica (>= 100 moedas)'
                                   'Depósito de moedas ao balcão', 'Depósito de dinheiro ao balcão',
                                  'Depósito em moeda metálica (>= 100 moedas)' ],
            'change_holder':['Alteração de titulares', 'Alteração de titularidade', 'Comissão de Alteração de Titularidade',
                                     'Alteração de titularidade / intervenientes', 'Alteração de titularidade (titular/ representante)'],
            'bank_overdraft':['Comissões por descoberto bancário', 'Descoberto bancário',
                             'Comissões por Descoberto Bancário'],
            'movement_consultation':['Consulta de Movimentos de conta DO com', 'Consulta de movimentos ao balcão'],
            'balance_inquiry':['Pedido de saldo ao balcão', 'Consulta de Saldo de conta DO com comprovativo']
           }


subproduct_dict = {'statement' : None,
                    'documents_copy' : None,
                    'acc_manteinance' : None,
                    'withdraw': None,
                    'online_service' : None,
                    'cash_deposit': None,
                    'change_holder' : None,
                    'bank_overdraft': None,
                    'movement_consultation': None,
                    'balance_inquiry': None}




class DemandDeposit:
    def __init__(self, link, page):
        self.link = link
        self.page = page

    def get_pdf(self):
        remote = urlopen(Request(self.link)).read()
        memory = BytesIO(remote)
        return memory


    def getting_text(self):
        file = pdfplumber.open(self.get_pdf())
        if len(self.page) > 1 :
            joined_text = []
            for el in self.page:
                page = file.pages[el]
                text = page.extract_text()
                joined_text.append(text)
            text ='             NEXT          '.join(joined_text)
            text = text.replace('Isento', '0,00')
            text = text.replace('n/a', '0,00')
            text = re.sub('--', str(np.nan), text)
            return text
        else:
            page = file.pages[self.page[0]]
            text = page.extract_text()
            text = text.replace('Isento', '0,00')
            text = text.replace('n/a', '0,00')
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
                        if '[0-9]{1-2},[0-9]{2}' in sentence:
                            if value in lista:
                                lista[value].append(sentence)
                            else:
                                lista[value]= [sentence]
                        else:
                            if value in lista:
                                lista[value].append(' '.join([sentence,file[ind+1]]))
                            else:
                                lista[value]= [' '.join([sentence,file[ind+1]])]
        if lista == {}:
            return 'not the right page'
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
        if len(self.n_account()[0]) > 20:
            return self.n_account()
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
        lista =[]
        for name in regular:
            single = ' '.join(name.split(" ")[:2])
            if single not in lista:
                lista.append(name)
        return lista

    def accounts_offer(self):

        return len(self.names())


    def indexes(self):
        complete_text = self.tokenize()
        indexes_name = {}
        indexes_value = {}
        for name in self.names():
            for inx,sentence in enumerate(complete_text):
                if name in sentence:
                    if name in indexes_name:
                        indexes_name[name].append(inx)
                    else:
                        indexes_name[name] = [inx]
        for lista in com_dict.values():
            for value in lista:
                for inx,sentence in enumerate(complete_text):
                    if value in sentence:
                        if value in indexes_value:
                            indexes_value[value].append(inx)
                        else:
                            indexes_value[value] = [inx]
        return indexes_name, indexes_value

    def values_sentence(self):
        sentence_account = {}
        values = self.indexes()[1]
        names = self.indexes()[0]
        text = self.tokenize()
        for conta,idx in names.items():
            idx = idx[0]
            closer = 0
            types ={}
            for commission,number_comm in values.items():
                for element in number_comm:
                    if element >= idx and (element<closer or closer == 0):
                        closer = element
                        if r'(\d+,\d{2})' not in text[element]:
                            sentence = text[element]
                            sentence = ' '.join([sentence, text[element+1]])
                            price = re.search(r'(\d+,\d{2})',sentence)
                            if price:
                                found = price.group()
                                types[commission] = found
                        else:
                            price = re.search(r'(\d+,\d{2})',sentence)
                            if price:
                                found = price.group()
                                types[commission]= text[found]
                sentence_account[conta] = types
        return sentence_account

    def complete_info(self):
        sentence_account = self.values_sentence()
        sentence_account['General']={}
        values_bank = self.values()
        commissions = [objects.keys() for k,objects in sentence_account.items()]
        for k,sentences in values_bank.items():
            if k not in commissions:
                sentence = sentences[0]
                price = re.search(r'(\d+,\d{2})',sentence)
                if price:
                    found = price.group()
                    sentence_account['General'][k]=found
        return sentence_account


    def demand_depos(self):
        finals = {}
        for account, dictionary in self.complete_info().items():
            demand_depos = {}
            for k in dictionary:
                for eng, value in com_dict.items():
                    if k in value:
                        demand_depos[eng] = dictionary[k]
            finals[account]=demand_depos
        return finals


    def output(self):
        output = {'demand_depos':{}}
        output['demand_depos']['subroducts'] = self.demand_depos()
        output['demand_depos']['n_subproducts']= self.accounts_offer()
        output['house_credit'] = {}
        output['term_depos'] = {}
        return output
