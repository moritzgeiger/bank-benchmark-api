import flask
from flask import request, jsonify
import requests
import os
import time
import json
from threading import Thread
# from rq import Connection, Queue, Worker
# from redis import Redis
import markdown.extensions.fenced_code
import markdown.extensions.codehilite
from pygments.formatters import HtmlFormatter
import markdown
from urllib.parse import urljoin
import random

### importing classes
from bank_benchmark_api.uploader import PdfUploader
from bank_benchmark_api.sourcing import PdfSourcing
from bank_benchmark_api.pagefinder import PageFinder
from bank_benchmark_api.demand_deposit_scrap import DemandDeposit
from bank_benchmark_api.housecredit import HouseCredit


# # google creds ## lalala
# credential_path = "/Users/moritzgeiger/code/.gcp/WAGON_KEY_MG.json"
# os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path

## where to send the results
app_base = 'https://matrix-pwc.herokuapp.com/'
app_endpoint = 'hub'

## init app
app = flask.Flask(__name__)
app.config["DEBUG"] = True

## adding endpoints
@app.route('/', methods=['GET'])
def home():
    readme_file = open("README.md", "r")
    md_template_string = markdown.markdown(
    readme_file.read(), extensions=["fenced_code", "codehilite"]
    )

    # Generate Css for syntax highlighting
    formatter = HtmlFormatter(style="emacs",full=True,cssclass="codehilite")
    css_string = formatter.get_style_defs()
    md_css_string = "<style>" + css_string + "</style>"

    md_template = md_css_string + md_template_string
    return md_template

#########################
##### BANK DETAILS ######
#########################

@app.route('/merge_pdfs', methods=['POST'])
def merge_pdfs():
    print('merge_pdfs was called')
    requirements = ['url', 'bp_bank_id', 'last_updated']
    validator = []
    r = request.json
    for vals in r.values():
        print(f'checking if requirements for each bank are in {vals.keys()}')
        val_bank = all([x in vals.keys() for x in requirements])
        validator.append(val_bank)
    print(f'matched these positions in keys: {validator}')

    if all(validator):
        # moving sourcing tasks to the background so that rails app has a quick response
        # setting unique identifier for the requested job. will be needed later for file pickup
        ident = random.randint(100,999)
        def start_sourcing_and_merging(r):
            # runs all the sourcing jobs and prepares for the merging job
            sourcing = PdfSourcing(r)
            print(f'pdf sourcing job was called.')
            banks = sourcing.rerun_sourcing()

            # forwarding banks to the merging job
            merging = PdfUploader(banks)
            # print(f'pdf merging and uploading job was called.')
            banks = merging.pdf_uploader()
            #
            with open(f'bank_benchmark_api/data/banks_{ident}.json', 'w') as file:
                json.dump(banks, file)

            # r = requests.post(url=urljoin(app_base, app_endpoint), )
            print(f'updated bank.json ready for pickup with ident: {ident}')


        thread = Thread(target=start_sourcing_and_merging, kwargs={'r': r})
        print(f'starting thread for job: {thread.name}, ident: {ident}')
        thread.start()

        return jsonify({'status':'ok', 'thread_name': str(thread.name), 'started': True, 'ident':ident})

    else:
        return jsonify({ 'status': 'error', 'message': f'one of these required keys were not passed {requirements}'})


@app.route('/get_stats', methods=['POST'])
def get_stats():
    print('get_stats was called')
    requirements = [
        'bp_pdf_url',
        'bp_bank_id',
        'cloud_merged_url',
        'products',
        'url',
    ]
    validator = []
    r = request.json
    for vals in r.values():
        print(f'checking if requirements for each bank are in {vals.keys()}')
        val_bank = all([x in vals.keys() for x in requirements])
        validator.append(val_bank)
    print(f'matched these positions in keys: {validator}')

    if all(validator):
        # moving sourcing tasks to the background so that rails app has a quick response
        ident = random.randint(1000, 9999)

        def start_pagefinder_pricescraping(r):
            # runs all the page finding jobs and scraping prices for each requested bank
            banks = {}
            for i, val in r.items():
                pagefinder = PageFinder(val)
                bank = pagefinder.find_page()
                # forwarding the bank to the scraping job
                demand_deposit = DemandDeposit(bank).output()
                banks[i] = {'products':{}}
                banks[i]['products']['demand_deposit'] = demand_deposit
                print(
                    f'finished job for demand deposits and injecting results in response: {demand_deposit}'
                )
                housing_credit = HouseCredit(bank).scrape_all()
                banks[i]['products']['housing_credit'] = housing_credit
                print(
                    f'finished job for housing credits and injecting results in response: {housing_credit}'
                )


            path = f'bank_benchmark_api/data/banks_{ident}.json'
            with open(path, 'w') as file:
                json.dump(banks, file)

                # r = requests.post(url=urljoin(app_base, app_endpoint), )
                print(f'price infos banks_{ident}.json ready to be picked up. at /retrievestats')

        thread = Thread(target=start_pagefinder_pricescraping, kwargs={'r': r})
        print(f'starting thread for job: {thread.name}')
        thread.start()

        return jsonify({
            'status': 'ok',
            'thread_name': str(thread.name),
            'started': True,
            'ident':ident
        })

    else:
        return jsonify({
            'status':
            'error',
            'message':
            f'one of these required keys were not passed: {requirements}'
        })



@app.route('/retrievepdfs', methods=['GET'])
def retrieve_pdfs():
    print('retrieve_pdfs was called')
    if 'ident' in request.args:
        ident = int(request.args['ident'])
        try:
            time.sleep(5)
            path = f'bank_benchmark_api/data/banks_{ident}.json'
            with open(path) as json_file:
                banks = json.load(json_file)
            os.remove(path)
            print(f'bank json {ident} loaded, supplied and removed from server')
            return banks

        except Exception as e:
            print(f'{ident} is not available on server. Error: {e}')
            return jsonify({'status':'error', 'message': f'sourcing job not finished or initialized or ident: {ident} is not available. first call /merge_pdfs and wait for backgroundjob to finish. Error msg: {e}'})

    else:
        return jsonify({'status':'error', 'message': 'please provide identifier "ident" as argument'})


@app.route('/retrievestats', methods=['GET'])
def retrieve_stats():
    print('retrieve_stats was called')
    if 'ident' in request.args:
        ident = int(request.args['ident'])
        try:
            time.sleep(5)
            path = f'bank_benchmark_api/data/banks_{ident}.json'
            with open(path) as json_file:
                banks = json.load(json_file)
            os.remove(path)
            print(
                f'bank price json with {ident} loaded, supplied and removed from server')
            return banks

        except Exception as e:
            return jsonify({
                'status':
                'error',
                'message':
                f'sourcing job not finished or initialized or ident: {ident} is not available. first call /get_stats and wait for backgroundjob to finish. Error msg: {e}'
            })

    else:
        return jsonify({
            'status':
            'error',
            'message':
            'please provide identifier "ident" as argument'
        })

#############################
###### TESTING ENDPOINTS ####
#############################



### fun
@app.route('/meme', methods=['GET'])
def meme():
    return '<img src="https://wyncode.co/uploads/2014/08/121.jpg">'


@app.route('/ping', methods=['GET'])
def pong():
    return 'pong'


@app.route('/double', methods=['GET'])
def double():
    # Check if an ID was provided as part of the URL.
    # If ID is provided, assign it to a variable.

    # If no ID is provided, display an error in the browser.
    if 'number' in request.args:
        number = int(request.args['number'])
    else:
        return "Error: No id field provided. Please specify an id."

    return str(number + number)

@app.route('/reverse', methods=['GET'])
def reverse():
    # Check if a word was provided as part of the URL.
    # If word is provided, assign it to a variable.
    # If no word is provided, display an error in the browser.
    if 'word' in request.args:
        word = request.args['word']
    else:
        return "Error: No id field provided. Please specify a word."

    return word[::-1]

## run app
if __name__ == '__main__':
    app.run()
