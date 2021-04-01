import flask
from flask import request, jsonify
import requests


### importing classes
from bank_benchmark_api.add_bank import AddBank
# from bank_benchmark_api.sourcing import PdfSourcing
from bank_benchmark_api.sourcing_each import PdfSourcing

## init app
app = flask.Flask(__name__)
app.config["DEBUG"] = True

## adding endpoints
@app.route('/', methods=['GET'])
def home():
    return '''<h1>Welcome to the benchmark API</h1>
                <p>A prototype API to get banking prices.</p>
                <p>endpoint: allbanks (returns all banks and pdf urls)</p>
                <p>endpoint: addbank (adds a banks to the db)</p>
                <p>endpoint: rmbank (removes bank from db)</p>
                <p>endpoint: meme (returns a meme)</p>
                <p>endpoint: ping (returns "pong")</p>
                <p>endpoint: double (returns number x 2)</p>
                <p>endpoint: reversed (returns string reversed)</p>'''
### fun
@app.route('/meme', methods=['GET'])
def meme():
    return '<img src="https://wyncode.co/uploads/2014/08/121.jpg">'

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
    print('add_bank was called')
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
    print('all_banks was called')
    sourcing = PdfSourcing()
    banks = sourcing.rerun_sourcing()
    return banks

@app.route('/rmbank', methods=['GET'])
def rm_bank():
    print('rm_bank was called')
    if 'name' in request.args:
        name = request.args['name']
        removing = AddBank()
        try:
            removing.rm_bank(name)
            return {'message':f'bank {name} has been removed from the database'}
        except:
            return {'error': {'message':f'name {name} does not exist in database'}}
    else:
        return {'error': {'message':'no bank name provided'}}


@app.route('/getpdfs', methods=['POST'])
def get_pdfs():
    print('get_banks was called')
    requirements = ['url', 'name', 'num_pdfs', 'last_updated', 'sum_sizes', 'bp_bank_id']
    validator = []
    r = request.json
    print(f'validating request keys')
    for k, v in r.items():
        print(f'checking if requirements are in {v.keys()}')
        validator.append([x in v.keys() for x in requirements])
    print(validator)
    if all(validator):
        return 'good'
    
    else:
        return f'one of these keys were not passed {requirements}'


## run app
if __name__ == '__main__':
    app.run()