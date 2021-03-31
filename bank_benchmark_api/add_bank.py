import pandas as pd
import numpy as np
import requests
from PyPDF2 import PdfFileReader, PdfFileMerger, PdfFileWriter
import PyPDF2
from bs4 import BeautifulSoup
import os
import shutil
from urllib.parse import urljoin
from urllib.request import Request, urlopen
from io import StringIO, BytesIO
import cloudinary.uploader
import json



class AddBank:
    def __init__(self):
        pass

    ## Building an initial dictionary which is maintained in the backoffice of the app via input field.
    def input_details(name_bank, url):
        ## LOAD BANKS .json
        with open('../raw_data/banks.json') as json_file:
            banks = json.load(json_file)
        
        ## INSPECT INPUT
        if 'http' in url:
            pass
        else:
            url = 'https://' + url
        url = url.strip("/")
        banks[name_bank] = {'url':url}

        ## SAVE BANK.json back to directory
        with open('../raw_data/banks.json', 'w') as fp:
            json.dump(banks, fp)