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
                    "Emissão de extrato",
                    "Extrato Integrado",
                    "Extrato Mensal",
                    "Extrato integrado",
                    "Extrato avulso"
                ],
                "documents_copy": [
                    "Fotocópias de segundas vias de talões de depósito",
                    "Emissão 2ªs Vias de Avisos e Outros Documentos",
                    "Extracto avulso",
                    "Segundas vias (pedido na agência)"
                ],
                "acc_manteinance": [
                    "Manutenção de conta",
                    "Comissão de manutenção de conta",
                    "Comissão de Manutenção de Conta",
                    "Manutenção de Conta Pacote",
                    "Manutenção de Conta Base",
                    "Manutenção de Conta Serviços Mínimos Bancários"
                ],
                "withdraw": [
                    "Levantamento de numerário",
                    "Levantamento de numerário ao balcão",
                    "Comissão de Levantamento",
                    "Levantamento de Numerário ao Balcão",
                    "Levantamento de Numerário ao Balcão"
                ],
                "online_service": [
                    "Adesão ao serviço de banca à distância",
                    "Adesão ao serviço online"
                ],
                "cash_deposit": [
                    "Depósito de moedas metálicas",
                    "Depósito de moedas",
                    " Depósito em moeda metálica (>= 100 moedas)",
                    "Depósito de moedas ao balcão",
                    "Depósito de dinheiro ao balcão",
                    "Depósito em moeda metálica (>= 100 moedas)"
                ],
                "change_holder": [
                    "Alteração de titulares",
                    "Alteração de titularidade",
                    "Comissão de Alteração de Titularidade",
                    "Alteração de titularidade / intervenientes",
                    "Alteração de titularidade (titular/ representante)"
                ],
                "bank_overdraft": [
                    "Comissões por descoberto bancário",
                    "Descoberto bancário",
                    "Comissões por Descoberto Bancário"
                ],
                "movement_consultation": [
                    "Consulta de Movimentos de conta DO com",
                    "Consulta de movimentos ao balcão"
                ],
                "balance_inquiry": [
                    "Pedido de saldo ao balcão",
                    "Consulta de Saldo de conta DO com comprovativo"
                ]
                },
                "portuguese": "Contas de Depósito"
            },
            "housing_credit": "portuguese": "Crédito à habitação e outros créditos hipotecários"
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
                                      "subproduct2": {
                                                      "commission1": "123",
                                                      "commission2": "345"
                                                      }
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


--------------------------
# GET /retrievestats

retrieve the scraping job results you have requested from /get_stats (takes a couple of minutes).
mandatory argument: 'ident' => pass the 4-digit number you were given from the /merge_pdfs immediate response.

-------------
