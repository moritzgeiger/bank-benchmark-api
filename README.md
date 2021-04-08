# Welcome to the Bank Price API docs

BASE URL: https://bank-price-api.herokuapp.com


# Rails perspective:
```
  Click a button --> POST localhost:3000/banks/c/check_updates

  banks_controller.rb

  require 'open-uri'

  def check_updates
    bank = Bank.find(....)
    payload1 = { bank.id: 44, ... }

    serialized = open('https://bank-price-api.herokuapp.com/merge_pdfs', method: 'POST', data: payload1)

    data = JSON.parse(serialized)

    if data[id]['status'] == 'ok'
        payload2 = { <bank.id>: ...., 'key2': ... }
        serialized = open('https://bank-price-api.herokuapp.com/get_stats', method: 'POST', data: payload2)
    else
      TODO
    end

    redirect_to bank_path(bank)
  end


routes.rb

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
          { <bank.id>: {
              'url': 'www.abanca.pt',
              'bp_bank_id': <bank.bp_id>
              'num_pdfs': 2,
              'last_updated': < bank.documents.sort('created_at').last >,
              'cloud_merged_url': 'https://www.cloudinary.ao/mega_mega_file_merged_bp0038.pdf',
              'products': [
                    {
                      'demand_deposit': comm_hash_1,
                      'pages': [3,4] (from merged pdf)
                    },
                    {
                      'housing_credit': comm_hash_2,
                      'pages': [9] (from merged pdf)
                    }
                ]
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
-------------


Comission hash:
```
comm_hash_1 =
{'EmissÃ£o de Extrato': ['EmissÃ£o de extrato',
  'Extrato Integrado',
  'Extrato Mensal'],
 'FotocÃ³pias e 2Âªvias': ['FotocÃ³pias de segundas vias de talÃµes de depÃ³sito',
  'EmissÃ£o 2Âªs Vias de Avisos e Outros Documentos',
  'Extracto avulso',
  'Segundas vias (pedido na agÃªncia)'],
 'ManutenÃ§Ã£o de Conta': ['ManutenÃ§Ã£o de conta',
  'ComissÃ£o de manutenÃ§Ã£o de conta'],
 'Levantamento de NumerÃ¡rio': ['Levantamento de numerÃ¡rio',
  'Levantamento de numerÃ¡rio ao balcÃ£o'],
 'AdesÃ£o ao ServiÃ§o Online': ['AdesÃ£o ao serviÃ§o de banca Ã  distÃ¢ncia',
  'AdesÃ£o ao serviÃ§o online'],
 'DepÃ³sitos de Moedas': ['DepÃ³sito de moedas metÃ¡licas',
  'DepÃ³sito de moedas',
  'DepÃ³sito de moedas ao balcÃ£o',
  'DepÃ³sito de dinheiro ao balcÃ£o',
  'DepÃ³sito de moeda metÃ¡lica (â‰¥ a 100 moedas)'],
 'AteraÃ§Ã£o de Titulares': ['AlteraÃ§Ã£o de titulares',
  'AlteraÃ§Ã£o de titularidade',
  'AlteraÃ§Ã£o de titularidade / intervenientes'],
 'Descoberto BancÃ¡rio': ['ComissÃµes por descoberto bancÃ¡rio',
  'Descoberto bancÃ¡rio'],
 'Consulta de Movimentos': ['Consulta de Movimentos de conta DO com',
  'Consulta de movimentos ao balcÃ£o'],
 'Consulta de Saldo': ['Pedido de saldo ao balcÃ£o',
  'Consulta de Saldo de conta DO com comprovativo']
}

```
