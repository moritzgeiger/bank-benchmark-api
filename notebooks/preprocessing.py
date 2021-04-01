import pandas as pd
import numpy as np
import pdfplumber

def new_df(x):
            return x.replace(np.nan, '*')

class Ordem:
    def __init__(self, pdf_file):
        self.pdf = pdfplumber.open(pdf_file)
    def get_df(self,page,columns, keys, strategy, row):
        pages = self.pdf.pages
        table = pages[page].extract_table(table_settings= {"horizontal_strategy": strategy, "keep_blank_chars": True,"text_y_tolerance": 10, 'text_x_tolerance':20})
        df = pd.DataFrame(table)
        df=df.drop(columns)
        df= df.apply(new_df, axis = 1)
        df = df.set_index(keys)
        if row == None:
            return df
        return df.drop(row)
