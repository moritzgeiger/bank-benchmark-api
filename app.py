import flask
from flask import request, jsonify
import requests
import os
import time
import json
from threading import Thread
from rq import Connection, Queue, Worker
from redis import Redis
import markdown.extensions.fenced_code
import markdown


### importing classes
from bank_benchmark_api.uploader import PdfUploader
# from bank_benchmark_api.sourcing import PdfSourcing
from bank_benchmark_api.sourcing import PdfSourcing


## init app
app = flask.Flask(__name__)
app.config["DEBUG"] = True

## adding endpoints
@app.route('/', methods=['GET'])
def home():
    readme_file = open("README.md", "r")
    return markdown.markdown(readme_file.read(), extensions=["fenced_code"])



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
        print(f'checking if requirements are in {vals.keys()}')
        validator.append([x in vals.keys() for x in requirements])
    validator = [j for i in validator for j in i]
    print(f'matched these positions in keys: {validator}')

    if all(validator):
        # moving sourcing tasks to the background so that rails app has a quick reaponse

        def start_task_sourcing(r):
            # runs all the sourcing jobs and then dumps jsonfile to 'bank_benchmark_api/data/banks.json
            sourcing = PdfSourcing(r)
            sourcing.rerun_sourcing()
        thread = Thread(target=start_task_sourcing, kwargs={'r': r})
        thread.start()

        return jsonify({'status':'ok', 'thread_name': str(thread.name), 'started': True})
    else:
        return {'error': f'one of these required keys were not passed {requirements}'}

# only runs with the list of pdfs provided from /dopdfs!
@app.route('/uploadpdfs', methods=['POST'])
def upload_pdfs():
    print('upload_pdfs was called')
    requirements = ['url', 'name', 'num_pdfs', 'list_pdfs', 'cloud_url_size', 'cloud_url', 'last_updated', 'bp_bank_id']
    validator = []
    r = request.json
    for vals in r.values():
        print(f'checking if requirements are in {vals.keys()}')
        val_bank = all([x in vals.keys() for x in requirements])
        validator.append(val_bank)
    # validator = [j for i in validator for j in i]
    print(f'matched these positions in keys: {validator}')

    if all(validator):
        # moving sourcing tasks to the background so that rails app has a quick reaponse

        def start_task_uploading(r):
            # runs all the sourcing jobs and then dumps jsonfile to 'bank_benchmark_api/data/banks.json
            uploader = PdfUploader(r)
            uploader.pdf_uploader()

        ## use rq library
        thread = Thread(target=start_task_uploading, kwargs={'r':r})
        thread.start()
        return {'message': 'uploading initialized. Go to /retrievepdfs to pick up requested data'}

    else:
        return {'error': f'one of these required keys were not passed {requirements}'}

@app.route('/retrievepdfs', methods=['GET'])
def retrieve_pdfs():
    print('retrieve_pdfs was called')
    try:
        time.sleep(5)
        with open('bank_benchmark_api/data/banks.json') as json_file:
            banks = json.load(json_file)
        os.remove('bank_benchmark_api/data/banks.json')
        print(f'bank json loaded, supplied and removed from server')
        return banks

    except Exception as e:
        return f'{{error: sourcing job not finished or initialized. first call /dopdfs and wait for backgroundjob to finish. Error msg: {e}}}'

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
