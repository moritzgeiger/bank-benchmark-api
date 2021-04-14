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
            'cash_deposit':['Depósito de moedas metálicas', 'Depósito de moedas', ' Depósito em moeda metálica (>= 100 moedas)',
                                   'Depósito de moedas ao balcão', 'Depósito de dinheiro ao balcão',
                                  'Depósito em moeda metálica (>= 100 moedas)' ],
            'change_holder':['Alteração de titulares', 'Alteração de titularidade', 'Comissão de Alteração de Titularidade',
                                     'Alteração de titularidade / intervenientes', 'Alteração de titularidade (titular/ representante)'],
            'bank_overdraft':['Comissões por descoberto bancário', 'Descoberto bancário',
                             'Comissões por Descoberto Bancário'],
            'movement_consultation':['Consulta de Movimentos de conta DO com', 'Consulta de movimentos ao balcão'],
            'balance_inquiry':['Pedido de saldo ao balcão', 'Consulta de Saldo de conta DO com comprovativo']
           }


# subproduct_dict = {'statement' : None,
#                     'documents_copy' : None,
#                     'acc_manteinance' : None,
#                     'withdraw': None,
#                     'online_service' : None,
#                     'cash_deposit': None,
#                     'change_holder' : None,
#                     'bank_overdraft': None,
#                     'movement_consultation': None,
#                     'balance_inquiry': None}




class DemandDeposit:
    def __init__(self, link, page):
        self.link = link
        self.page_demand = page
#         self.id_bank = id_bank
#         self.dict_demand = com_dict
# class DemandDeposit:
#     def __init__(self,dictionary):
#         self.dict_demand = dictionary['products']['demand_deposit']
#         self.page_demand = dictionary['products']['pages']
#         self.link = dictionary['bp_pdf_url']
#         self.id_bank = dictionary['bp_bank_id']
    def is_avaiable(self):
        if self.page_demand == None:
            print(f'This main product is not avaiable for the following bank: {self.link}')
        else:
            return self

    def get_pdf(self):
        remote = urlopen(Request(self.link)).read()
        memory = BytesIO(remote)
        return memory


    def getting_text(self):
        file = pdfplumber.open(self.get_pdf())
        if len(self.page_demand) > 1 :
            joined_text = []
            for el in self.page_demand:
                page = file.pages[el]
                text = page.extract_text()
                joined_text.append(text)
            text ='             NEXT          '.join(joined_text)
            text = text.replace('Isento', '0,00')
            text = text.replace('n/a', '0,00')
            text = re.sub('--', str(np.nan), text)
            return text
        else:
            page = file.pages[self.page_demand[0]]
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
        tokenized = self.tokenize()
        values = [x for x in self.dict_demand.values()]
        lista ={}
        for commission in values:
            for value in commission:
                for ind,sentence in enumerate(tokenized):
                    if value in sentence:
                        if '[0-9]{1-2},[0-9]{2}' in sentence:
                            if value in lista:
                                lista[value].append(sentence)
                            else:
                                lista[value]= [sentence]
                        else:
                            if value in lista:
                                lista[value].append(' '.join([sentence, tokenized[ind+1]]))
                            else:
                                lista[value]= [' '.join([sentence,tokenized[ind+1]])]
        if lista == {}:
            return 'not the right page'
        return lista

    def n_account(self):
        accounts = []
        finals = []
        tokenized = self.tokenize()
        text = self.getting_text()
        if len(nltk.sent_tokenize(text)) < 15 :
            for sentence in tokenized:
                if 'Conta' in sentence:
                    finals.append(sentence)
            return finals
        for sentence in tokenized:
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

        return len(self.specific_bank().keys())-1


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
        for lista in self.dict_demand.values():
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
                        if r'(\d{1,2},\d{2})' not in text[element]:
                            sentence = text[element]
                            sentence = ' '.join([sentence, text[element+1]])
                            price = re.search(r'(\d{1,2},\d{2})',sentence)
                            if price:
                                found = price.group()
                                types[commission] = found
                        else:
                            price = re.search(r'(\d{1,2},\d{2})',sentence)
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
                price = re.search(r'(\d{1,2},\d{2})',sentence)
                if price:
                    found = price.group()
                    sentence_account['General'][k]=found
        return sentence_account

    def specific_bank(self):
        complete_info = self.complete_info()

        if self.id_bank == '0269':
            # """bankinter"""
            for v in complete_info.values():
                if v['Comissão de Manutenção de Conta'] == '0,00':
                    v['Comissão de Manutenção de Conta'] = '80,00'
            return complete_info

        elif self.id_bank == '0170':
            # abanca
            complete_text = self.getting_text()
            accounting_idx = complete_text.find('Manutenção de conta') - len(complete_text)-1
            accounting = complete_text[accounting_idx:]
            abanca_last = self.complete_info()
            for name in abanca_last:
                inx = accounting.find(name) - len(accounting)-1
                new_text = accounting[inx:]
            #     print(new_text, 'AAAAAAAAAAAAAAA')
                value = re.search(r'(\d{1,2},\d{2})',new_text)
                if value:
                    found = value.group()
                    abanca_last[name]['Manutenção de conta'] = found
            return abanca_last

        elif self.id_bank == '0008':
            # bai
            complete_info['Conta de Serviços Mínimos Bancários Comissões vigência contrato ']={}
            complete_info['Conta de Serviços Mínimos Bancários Comissões vigência contrato ']['Manutenção de conta']= '5,00'
            complete_info['General']['Extrato integrado'] = '0,00'
            complete_info.pop('Conta de Serviços Minímos Bancários: Condições de acesso: Particulares residentes num Estado Membro da')
            complete_info.pop('Conta de Serviços Mínimos Bancários não depende da aquisição de outros produtos ou serviços.')
            return complete_info

        elif self.id_bank == '0079':
            # bic
            for name,v in complete_info.items():
                for k in v:
                    if v[k] == '00,00':
                        v[k]= '9,30'
            complete_info['Conta à Ordem com Futuro 0,00 nan Nota 4']['Comissão de manutenção de conta']='0,00'
            complete_info['Conta Cool (contratações a partir de 13 de novembro 2014) 0,00 nan Notas 4,']['Comissão de manutenção de conta'] = '0,00'
            complete_info['Conta à Ordem Massa Insolvente 0,00 nan Nota 14']['Comissão de manutenção de conta'] = '0,00'
            return complete_info

        elif self.id_bank == '0193':
            # ctt
            complete_info.pop('Banco CTT, S.A. Contas de Depósito-Particulares - Pág.1/2')
            return complete_info
        else:
            return complete_info




    def demand_depos(self):
        finals = {}
        for account, dictionary in self.specific_bank().items():
            demand_depos = {}
            for k in dictionary:
                for eng, value in self.dict_demand.items():
                    if k in value:
                        demand_depos[eng] = dictionary[k]
            finals[account]=demand_depos
        return finals


    def output(self):
        output = {'demand_depos':{}}
        output['demand_depos']['subproducts'] = self.demand_depos()
        output['demand_depos']['n_subproducts']= self.accounts_offer()
        # output['house_credit'] = {}
        # output['term_depos'] = {}
        return output
