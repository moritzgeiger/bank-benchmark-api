# Endpoints
This is how your request should look like - you can request as many banks as you wish:
```
{'4': {'bp_bank_id': '0008',
      'bp_pdf_url': 'https://clientebancario.bportugal.pt/sites/default/files/precario/0008_/0008_PRE.pdf',
      'last_updated': '2021-04-06',
      'list_pdfs': ['https://www.bancobai.ao/media/2988/bai_pre_clientes-particulares_31-03-2021.pdf',
       'https://www.bancobai.ao/media/2989/bai_pre_outros-clientes_31-03-2021.pdf',
       'https://www.bancobai.ao/media/2823/bai_resumo-das-alteracoes-do-precario-bna-8-02-2021-cleaned.pdf',
       'https://www.bancobai.ao/media/2278/termos-e-condições.pdf'],
      'name': 'BAI - Banco Angolano de Investimentos.',
      'num_pdfs': 4,
      'price_page': 'https://www.bancobai.ao/pt/preçário',
      'cloud_url': "https://storage.googleapis.com/bank_price_pdfs/4_all_products.pdf",
      'cloud_url_size': "1975488",
      'url': 'https://www.bancobai.ao',
      'products': {'1.1': {'url':'https://clientebancario.bportugal.pt/sites/default/files/precario/0170_/0170_PRE.pdf',
                          'pages': ['5']},
                  }
                  {'17.1': {'url':'https://clientebancario.bportugal.pt/sites/default/files/precario/0170_/0170_PRE.pdf',
                          'pages': ['5']}
                  },
      'commissions': {'1': 'Emissão de extrato',
                     '2': 'Fotocópias de segundas vias de talões de depósito',
                     '3': 'Manutenção de conta',
                     '4': 'Levantamento de numerário',
                     '5': 'Adesão ao serviço de banca à distância',
                     '6': 'Depósito de moedas metálicas',
                     '7': 'Alteração de titulares'
                    },
      }
 }
```

If you initially don't have values for the shown keys, fill them with 'None', otherwise the API will return an error.
