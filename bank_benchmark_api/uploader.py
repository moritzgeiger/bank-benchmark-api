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
import json
from google.cloud import storage
from dotenv import load_dotenv, find_dotenv
from datetime import datetime
import ssl


# setting global gcloud specs
load_dotenv(find_dotenv())
GOOGLE_APPLICATION_CREDENTIALS = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

cloud = 'https://storage.cloud.google.com/'
bucket_name = "bank_price_pdfs"

class PdfUploader:
    def __init__(self, bank_dict):
        self.bank_dict = bank_dict
        self.bucket_name = bucket_name
        self.cloud = cloud

    # is needed for some files
    def file_decrypt(self, pdf_url, filename="tempe.pdf"):
        """Accepts pdf urls. Returns PyPDF2 FileReader Objects"""
        print(f'file_decrypt was called for {pdf_url}')
        ### banco bai is very needy. need to declare verify=False
        response = requests.get(pdf_url, verify=False)
        if response.status_code == 200:
            temp = open(filename, "wb")
            temp.write(response.content)
            ## important: have to close again
            temp.close()
            # copies the file in temp.pdf / decrypts it and replaces the old file
            command="cp "+filename+" temp.pdf; qpdf --password='' --decrypt temp.pdf "+filename+ "; rm temp.pdf"
            os.system(command)
            print('file decrypted (with qpdf)')
            #re-open the decrypted file
            pdfFile = PdfFileReader(filename)
            # removing tempe file
            os.remove(filename)
            return pdfFile
        else:
            print(f'{url} could not be reached with file_decrypt. Response: {response}')
            return None


    def upload_file(self, source_file_bytes, file_name_uploaded, bucket_name=None):
        """Uploads a bytes pdf file to the bucket and returns the cloud link."""
        print("upload_file was called")
        # defining bucket name
        if bucket_name is None:
            bucket_name = self.bucket_name

        # Building connection with gcs
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)

        # opening a blob/destination name
        blob = bucket.blob(file_name_uploaded)

        # init upload => timeout needs to be high for big files
        blob.upload_from_string(source_file_bytes, content_type='application/pdf', timeout = 500.0)

        print(f"file uploaded as {file_name_uploaded}.")
        return blob.public_url

    def pdf_uploader(self):
        '''loops through all requested banks, sends files to decryptor, merges them and uploadts them to cloud storage'''
        for id, values in self.bank_dict.items():
            print(f'handling pdfs from {values.get("price_page")}')
            # acessing the URLs inside the pdf list
            web_pdfs = values.get("list_pdfs").get('urls')
            # start the merger for each bank
            merger = PdfFileMerger()
            # trying to remotely parse the pdfs all pdf pages
            for pdf_url in web_pdfs:
                try:
                    # gcontext = ssl.SSLContext()
                    remote = requests.get(pdf_url, verify=False).content
                    memory = BytesIO(remote)
                    pdf_file = PdfFileReader(memory)
                    # check file encryption - if yes, call decrypter
                    if pdf_file.isEncrypted:
                        print(f"file {pdf_url} is encrypted. \nstarting to decrypt and adding to merger.")
                        ## pass in web url string of the pdf
                        pdf_file = self.file_decrypt(pdf_url)
                        merger.append(pdf_file)
                        print(f'added file to pdf merger: {pdf_url}')
                    else:
                        print(
                            f"file is not encrypted: {pdf_url}  \nadding file to merger..."
                        )
                        merger.append(pdf_file)
                        print(f'added file to pdf merger: {pdf_url}')

                except Exception as e:
                    print(f"url not found. Error: {e}, url: {pdf_url}\nfile not added to merger.")

            # creating a bytes file to be uploaded
            temp = BytesIO()
            merger.write(temp)
            print(f'wrote merger file to BytesIO for: {values.get("url")}')
            print(f'size of BytesIO: {temp.getbuffer().nbytes}')
            values['list_pdfs']['cloud_url_size'] = f'{temp.getbuffer().nbytes}'

            # using gcs uploader function to upload bytes file
            file_name_uploaded = f'{id}_all_products_{datetime.now().strftime("%y%m%d%H%M%S")}.pdf'
            cloud_url = self.upload_file(temp.getvalue(), file_name_uploaded=file_name_uploaded)
            # closing everything for safe next loop
            temp.close()
            merger.close()
            print(f'uploaded merged file to cloud and cleared all memory: {file_name_uploaded}')
            values['list_pdfs']['cloud_merged_url'] = cloud_url
            print(f'updated banks dict with cloud link: {cloud_url}')

        print(f'pdf_uploader done. Json ready to be picked up by rails app via /retievepdfs')

        return self.bank_dict
