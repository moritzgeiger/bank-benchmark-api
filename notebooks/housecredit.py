import pandas as pd
import numpy as np
import pdfplumber
import re
import nltk
from urllib.parse import urljoin, quote_plus, quote, urlencode
from urllib.request import Request, urlopen
from io import StringIO, BytesIO

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

class HouseCredit:

    def __init__(self,link,page):
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
            text = text.replace('n/a', str(np.nan))
            text = re.sub('--', str(np.nan), text)
            return text
        else:
            page = file.pages[self.page[0]]
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
        values = [x for x in house_credit_com.values()]
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
        if lista == {}:
            return 'name of commisions not in database'
        return lista


    def n_account(self):
        accounts = []
        finals = []
        text = self.getting_text()
        if len(nltk.sent_tokenize(text)) < 15 :
            for sentence in self.tokenize():
                if 'Crédito Habitação' in sentence:
                    finals.append(sentence)
            return finals
        for sentence in self.tokenize():
            contas = re.split('Crédito Habitação',sentence)
            accounts.append(contas)
        for account in accounts:
            if len(account)>1:
                account = ['Crédito Habitação'+ x for x in account]
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
            if word[0] == 'Crédito Habitação' and len(word)>1 and word[1]!='nan':
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
