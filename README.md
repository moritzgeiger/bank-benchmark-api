# Welcome to the Bank Price API docs

BASE URL: https://bank-price-api.herokuapp.com

post 'banks/:id/merged_pdfs', to: 'banks#merged_pdfs'
post 'banks/:id/bank_stats', to:  'banks#bank_stats'
```

---------------------------------

# POST /merge_pdfs
```
  params:
    data:
          { <bank.id>: {
              'url': 'www.abanca.pt',
              'bp_bank_id': <bank.bp_id>
              'last_updated': < bank.documents.sort('created_at').last >
          }
```
    response:

          Status code 200 OK
```
          {'4': {
                  'status': 'ok',
                  'list_pdfs': {
                        'urls': [
                          'https://clientebancario.bportugal.pt/sites/default/files/precario/0008_/0008_PRE.pdf',
                          'https://www.abanca.ao/media/2988/bai_pre_clientes-particulares_31-03-2021.pdf',
                          'https://www.abanca.ao/media/2989/bai_pre_outros-clientes_31-03-2021.pdf',
                          'https://www.abanca.ao/media/2823/bai_resumo-das-alteracoes-do-precario-bna-8-02-2021-cleaned.pdf',
                          'https://www.abanca.ao/media/2278/termos-e-condiÃ§Ãµes.pdf'
                        ],
                        'cloud_merged_url': 'https://www.cloudinary.ao/mega_mega_file_merged_bp0038.pdf'
>>>>>>> b96fbe07a95da54efbe0025fed123d9c89cddec1
                  }
                }
          }
```
          Status code error
```
          {'4': { 'status': 'error', 'message': 'Ups! hello there'} }
```

--------------------------

# POST /get_stats
  params:
    data:
```
          { <bank.id1>: {
              'url': 'www.abanca.pt',
              'bp_bank_id': <bank.bp_id>,
              'bp_pdf_url': <bp_pdf_url>,
              'num_pdfs': 2,
              'last_updated': < bank.documents.sort('created_at').last >,
              'cloud_merged_url': 'https://www.cloudinary.ao/mega_mega_file_merged_bp0038.pdf',
              'products':
                            {
                              'demand_deposit': {'withdrawal':{'<conta base>:<price of conta base>}['Emissão de extrato', 'Extrato Integrado', 'Extrato Mensal'],
                                                'documents_copy':['Fotocópias de segundas vias de talões de depósito',
                                                'Emissão 2ªs Vias de Avisos e Outros Documentos', 'Extracto avulso',
                                                'Segundas vias (pedido na agência)'],
                                                },
                              'pages': [3,4] (from merged pdf)
                            },
                            {
                              'housing_credit': comm_hash_2,
                              'pages': [9] (from merged pdf)
                            }
                      },
            <bank.id2>: {
              'url': 'www.abanca.pt',
              'bp_bank_id': <bank.bp_id>,
              'bp_pdf_url': <bp_pdf_url>,
              'num_pdfs': 2,
              'last_updated': < bank.documents.sort('created_at').last >,
              'cloud_merged_url': 'https://www.cloudinary.ao/mega_mega_file_merged_bp0038.pdf',
              'products':
                            {
                              'demand_deposit': {<statement>:['Emissão de extrato', 'Extrato Integrado', 'Extrato Mensal'],
                                                'documents_copy':['Fotocópias de segundas vias de talões de depósito',
                                                'Emissão 2ªs Vias de Avisos e Outros Documentos', 'Extracto avulso',
                                                'Segundas vias (pedido na agência)'],
                                                },
                              'pages': [3,4] (from merged pdf)
                            },
                            {
                              'housing_credit': comm_hash_2,
                              'pages': [9] (from merged pdf)
                            }
                      }
          }
```

  response:

        Status code 200 OK
```
        {'4': {
                'status': 'ok',
                'bp_bank_id': '0008',
                'last_updated': '2021-04-06',
                'nr_pdfs': 3,
                'products': [
                ]

              }
        }
```
        Status code error
```
        {'4': { 'status': 'error', 'message': 'Ups! hello there'} }
```

-------------------------

# GET /retrievepdfs

retrieve the sourcing job you have requested from /merge_pdfs (takes a couple of minutes).
mandatory argument: 'ident' => pass the 3-digit number you were given from the /merge_pdfs immediate response.


--------------------------
# GET /retrievestats

retrieve the scraping job results you have requested from /get_stats (takes a couple of minutes).
mandatory argument: 'ident' => pass the 4-digit number you were given from the /merge_pdfs immediate response.

-------------
