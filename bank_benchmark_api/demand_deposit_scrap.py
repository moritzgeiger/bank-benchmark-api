import pandas as pd
import numpy as np
import pdfplumber
import re
import nltk
from urllib.parse import urljoin, quote_plus, quote, urlencode
from urllib.request import Request, urlopen
from io import StringIO, BytesIO

class DemandDeposit:
    def __init__(self,dictionary):
        self.dict_demand = dictionary['products']['demand_deposit']['commissions']
        self.page_demand = dictionary['products']['demand_deposit']['pages']
        self.link = dictionary['bp_pdf_url']
        self.id_bank = dictionary['bp_bank_id']

    def get_pdf(self):
        print(f'opening url: {self.link}...')
        remote = urlopen(Request(self.link)).read()
        memory = BytesIO(remote)
        return memory


    def getting_text(self, file):
        file = pdfplumber.open(file)
        print('extract pdf content to text...')
        print()
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


    def tokenize(self, text):
        print('tokenize text...')
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

    def values(self, tokenized):
        # tokenized = self.tokenize(file)
        values = [x for x in self.dict_demand.values()]
        print('find and compile all sentences with money values in them...')
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
            return {'error': f'wrong page/s provided {self.page_demand}'}
        # print(lista)
        return lista

    def n_account(self, tokenized, text):
        accounts = []
        finals = []
        # tokenized = self.tokenize(file)
        # text = self.getting_text(file)
        print('assign account names to sentences...')
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

    def names(self, tokenized, text):
        n_account = self.n_account(tokenized, text)
        if len(n_account[0]) > 20:
            return n_account
        words = []
        for account in n_account:
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

    def accounts_offer(self, specific_bank):

        return len(specific_bank.keys())-1


    def indexes(self, tokenized, text):
        complete_text = tokenized
        indexes_name = {}
        indexes_value = {}
        for name in self.names(tokenized, text):
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

    def values_sentence(self, tokenized, text):
        sentence_account = {}
        values = self.indexes(tokenized, text)[1]
        names = self.indexes(tokenized, text)[0]
        # text = self.tokenize(file)
        print('building sentence-value pairs')
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

    def complete_info(self, tokenized, text):
        sentence_account = self.values_sentence(tokenized, text)
        sentence_account['General']={}
        values_bank = self.values(tokenized)
        commissions = [objects.keys() for k,objects in sentence_account.items()]
        for k,sentences in values_bank.items():
            if k not in commissions:
                sentence = sentences[0]
                price = re.search(r'(\d{1,2},\d{2})',sentence)
                if price:
                    found = price.group()
                    sentence_account['General'][k]=found
        return sentence_account

    def specific_bank(self, tokenized, text):
        complete_info = self.complete_info(tokenized, text)
        print(f'dealing with bank specifics for this content: {complete_info}')

        if self.id_bank == '0269':
            # """bankinter"""
            if complete_info['General']['Comissão de Manutenção de Conta'] == '0,00':
                complete_info['General'][
                    'Comissão de Manutenção de Conta'] = '80,00'
            return complete_info

        elif self.id_bank == '0170':
            # abanca
            complete_text = text
            accounting_idx = complete_text.find('Manutenção de conta') - len(complete_text)-1
            accounting = complete_text[accounting_idx:]
            abanca_last = complete_info
            for name in abanca_last:
                inx = accounting.find(name) - len(accounting)-1
                new_text = accounting[inx:]
                #     print(new_text, 'AAAAAAAAAAAAAAA')
                value = re.search(r'(\d{1,2},\d{2})',new_text)
                if value:
                    found = value.group()
                    abanca_last[name]['Manutenção de conta'] = found
            popper = [
                "Conta que permite aceder aos seguintes produtos e serviços, mediante o pagamento de uma",
                "Conta para clientes sem crédito no ABANCA e com aplicações financeiras de valor inferior",
                "Conta para clientes dos 0 aos 28 anos.",
                "Conta regulada pelo Decreto-Lei n.º 27 C/2000, de 10 de março, com alterações posteriores."
            ]
            for pop in popper:
                abanca_last.pop(pop)
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
            if complete_info.get('Banco CTT, S.A. Contas de Depósito-Particulares - Pág.1/2'):
                complete_info.pop(
                    'Banco CTT, S.A. Contas de Depósito-Particulares - Pág.1/2'
                )
            return complete_info
        else:
            return complete_info




    def demand_depos(self, tokenized, text):
        finals = {}
        for account, dictionary in self.specific_bank(tokenized, text).items():
            demand_depos = {}
            for k in dictionary:
                print(f'parse product: {account}, fee {k}')
                for eng, value in self.dict_demand.items():
                    if k in value:
                        demand_depos[eng] = dictionary[k]
            finals[account]=demand_depos
        return finals


    def output(self):
        print('output was called')
        file = self.get_pdf()
        text = self.getting_text(file)
        tokenized = self.tokenize(text)
        output = {}
        output['subproducts'] = self.demand_depos(tokenized, text)
        specific_bank = self.specific_bank(tokenized, text)
        output['n_subproducts']= self.accounts_offer(specific_bank)
        # output['house_credit'] = {}
        # output['term_depos'] = {}
        return output
