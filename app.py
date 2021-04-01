import flask
from flask import request, jsonify
import requests


### importing classes
from bank_benchmark_api.add_bank import AddBank
from bank_benchmark_api.sourcing import PdfSourcing


## init app
app = flask.Flask(__name__)
app.config["DEBUG"] = True

## adding endpoints
@app.route('/', methods=['GET'])
def home():
    return '''<h1>Welcome to the benchmark API</h1>
                <p>A prototype API to get banking prices.</p>
                <p>endpoints: ping (returns "pong")</p>
                <p>endpoints: double (returns number x 2)</p>
                <p>endpoints: reversed (returns string reversed)</p>'''

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

@app.route('/bankstatus', methods=['GET'])
def bank_status():
    if 'url' in request.args:
        url = request.args['url']
        headers = {'Accept-Language': 'pt-PT'}
        response = requests.get(url, headers=headers)
        return {'status':response.status_code, 'url':url}
    else:
        return {'error': {'message':'no bank url provided'}}

@app.route('/pdfstatus', methods=['GET'])
def pdf_status():
    pass ## return pdf size or num of pdfs
    ## todo: what endpoints do we need
    # todo: route to check for new data


#########################
##### BANK DETAILS ######
#########################

@app.route('/addbank', methods=['GET'])
def add_bank():
    if all([x in request.args for x in ['name', 'url']]):
        url = request.args['url']
        name = request.args['name']
        adding = AddBank()
        adding.input_details(name, url)
        return {'status':f'bank {name} has been added/updated to the database'}
    else:
        return {'error': {'message':'no bank url or name provided'}}

@app.route('/allbanks', methods=['GET'])
def all_banks():
    sourcing = PdfSourcing()
    banks = sourcing.rerun_sourcing()
    return banks

@app.route('/geturls', methods=['GET'])
def get_urls():
    sourcing = PdfSourcing()
    banks = sourcing.get_pdf_urls()
    return banks



## run app
if __name__ == '__main__':
    app.run()