# Welcome to the Bank Price API docs

BASE URL: https://bank-price-api.herokuapp.com

This is an internal API open for communication with this bank pricing dashbard:
https://matrix-pwc.herokuapp.com/

The API can receive two kinds of requests to do the following jobs:
- Looking for PDFs on the internet which contain important bank price information and returning the files to the app.
- Scraping price data from given PDF files and reassembling it in a readable format.

---------------------------------

# POST /merge_pdfs
```
  params:
    data:
          {"5": {"bp_bank_id": "0193",
                "last_updated": "2021-04-06",
                "url": "https://www.bancoctt.pt/"
                }
                }
```
    response:

          Status code 200 OK
```
          {
            "5": {
              "bp_bank_id": "0193",
              "bp_pdf_url": "https://clientebancario.bportugal.pt/sites/default/files/precario/0193_/0193_PRE.pdf",
              "last_updated": "2021-04-14",
              "list_pdfs": {
                "cloud_merged_url": "https://storage.googleapis.com/bank_price_pdfs/5_all_products_210414140412.pdf",
                "cloud_url_size": "2216262",
                "urls": [
                  "https://www.bancoctt.pt/application/themes/pdfs/precario.pdf?language_id%3D1555597541833"
                ]
              },
              "num_pdfs": 1,
              "price_page": "https://www.bancoctt.pt/application/themes/pdfs/precario.pdf?language_id%3D1555597541833",
              "status": "ok",
              "url": "https://www.bancoctt.pt/"
            }
          }

```
          Status code error
```
          { 'status': 'error', 'message': 'one of these required keys were not passed <requirements>'}
```

--------------------------

# POST /get_stats
  params:
    data:
```
{
    "1": {
        "url": "www.abanca.pt",
        "bp_pdf_url": bp_pdf_url,
        "bp_bank_id": bp_bank_id,
        "cloud_merged_url": "https://storage.googleapis.com/bank_price_pdfs/1_all_products_210412130040.pdf",
        "products": {"demand_deposit": {"commissions":
                {
                    "statement": [
                    "Emiss??o de extrato",
                    "Extrato Integrado",
                    "Extrato Mensal",
                    "Extrato integrado",
                    "Extrato avulso"
                ],
                "documents_copy": [
                    "Fotoc??pias de segundas vias de tal??es de dep??sito",
                    "Emiss??o 2??s Vias de Avisos e Outros Documentos",
                    "Extracto avulso",
                    "Segundas vias (pedido na ag??ncia)"
                ],
                "acc_manteinance": [
                    "Manuten????o de conta",
                    "Comiss??o de manuten????o de conta",
                    "Comiss??o de Manuten????o de Conta",
                    "Manuten????o de Conta Pacote",
                    "Manuten????o de Conta Base",
                    "Manuten????o de Conta Servi??os M??nimos Banc??rios"
                ],
                "withdraw": [
                    "Levantamento de numer??rio",
                    "Levantamento de numer??rio ao balc??o",
                    "Comiss??o de Levantamento",
                    "Levantamento de Numer??rio ao Balc??o",
                    "Levantamento de Numer??rio ao Balc??o"
                ],
                "online_service": [
                    "Ades??o ao servi??o de banca ?? dist??ncia",
                    "Ades??o ao servi??o online"
                ],
                "cash_deposit": [
                    "Dep??sito de moedas met??licas",
                    "Dep??sito de moedas",
                    " Dep??sito em moeda met??lica (>= 100 moedas)",
                    "Dep??sito de moedas ao balc??o",
                    "Dep??sito de dinheiro ao balc??o",
                    "Dep??sito em moeda met??lica (>= 100 moedas)"
                ],
                "change_holder": [
                    "Altera????o de titulares",
                    "Altera????o de titularidade",
                    "Comiss??o de Altera????o de Titularidade",
                    "Altera????o de titularidade / intervenientes",
                    "Altera????o de titularidade (titular/ representante)"
                ],
                "bank_overdraft": [
                    "Comiss??es por descoberto banc??rio",
                    "Descoberto banc??rio",
                    "Comiss??es por Descoberto Banc??rio"
                ],
                "movement_consultation": [
                    "Consulta de Movimentos de conta DO com",
                    "Consulta de movimentos ao balc??o"
                ],
                "balance_inquiry": [
                    "Pedido de saldo ao balc??o",
                    "Consulta de Saldo de conta DO com comprovativo"
                ]
                },
                "portuguese": "Contas de Dep??sito"
            },
            "housing_credit": "portuguese": "Cr??dito ?? habita????o e outros cr??ditos hipotec??rios"
        }
    }
}
```

  response:

        Status code 200 OK
```
        {
  "1": {
    "products": {
      "demand_deposit": {
        "subproducts": {
          "Conta D.O.": {
            "statement": "0,00",
            "acc_manteinance": "15,00"
          },
          "Conta Ordenado": {
            "statement": "0,00",
            "acc_manteinance": "0,00"
          },
          "Conta Standard": {
            "statement": "0,00",
            "acc_manteinance": "0,00"
          },
          "Conta Future": {
            "statement": "0,00",
            "acc_manteinance": "0,00"
          },
          "Conta Kids": {
            "acc_manteinance": "0,00"
          },
          "Conta Base": {
            "statement": "0,00",
            "acc_manteinance": "10,00"
          },
          "Conta Private": {
            "statement": "0,00",
            "acc_manteinance": "8,00"
          },
          "Conta Value": {
            "statement": "0,00",
            "acc_manteinance": "5,00"
          },
          "Conta Smart": {
            "statement": "0,00",
            "acc_manteinance": "5,00"
          },
          "Conta Futuro": {
            "statement": "0,00",
            "acc_manteinance": "0,00"
          },
          "Conta Moeda Estrangeira e": {
            "statement": "0,00",
            "acc_manteinance": "15,00"
          },
          "Conta ABANCA Internacional.": {
            "statement": "0,00",
            "acc_manteinance": "15,00"
          },
          "Conta para clientes dos 18 aos 28 anos.": {
            "acc_manteinance": "0,23"
          },
          "Conta para clientes dos 0 aos 17 anos.": {
            "acc_manteinance": "0,23"
          },
          "Conta que permite aceder aos seguintes produtos e servi\u00e7os, mediante o pagamento de uma": {
            "acc_manteinance": "0,00"
          },
          "Conta para clientes sem cr\u00e9dito no ABANCA e com aplica\u00e7\u00f5es financeiras de valor inferior": {
            "acc_manteinance": "0,00"
          },
          "Conta para clientes dos 0 aos 28 anos.": {
            "acc_manteinance": "0,00"
          },
          "Conta regulada pelo Decreto-Lei n.\u00ba 27 C/2000, de 10 de mar\u00e7o, com altera\u00e7\u00f5es posteriores.": {
            "acc_manteinance": "0,00"
          },
          "General": {
            "statement": "0,00",
            "documents_copy": "5,00",
            "acc_manteinance": "10,00",
            "withdraw": "0,00",
            "online_service": "0,00",
            "cash_deposit": "3,50",
            "change_holder": "5,00"
          }
        },
        "n_subproducts": 18
      }
    },
    "housing_credit": {
                      "commissions": {
                                      "subproduct1": {
                                                      "commission1": "123",
                                                      "commission2": "345"
                                                      },
                                      "subproduct2": "123"
                                        }
                      }
  }
}
```
        Status code error
```
        {
            'status':
            'error',
            'message':
            'one of these required keys were not passed <requirements>'
        }
```

-------------------------

# GET /retrievepdfs

retrieve the sourcing job you have requested from /merge_pdfs (takes a couple of minutes).
mandatory argument: 'ident' => pass the 3-digit number you were given from the /merge_pdfs immediate response.
Example:
```https://bank-price-api.herokuapp.com/retrievepdfs?ident=123```

--------------------------
# GET /retrievestats

retrieve the scraping job results you have requested from /get_stats (takes a couple of minutes).
mandatory argument: 'ident' => pass the 4-digit number you were given from the /merge_pdfs immediate response.

-------------
