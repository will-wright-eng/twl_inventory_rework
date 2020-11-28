'''
utility file for common python fuctions
'''

import os
import re
import string

def list_files_in_directory(path):
    '''docstring for list_files_in_directory'''
    x = []
    cwd = os.getcwd()
    for root, dirs, files in os.walk('.'+path):
        for file in files:
            #print(root+'/'+file)
            x.append(root+'/'+file)
    return x

def process_cols_v2(cols):
    '''docstring for process_cols
    for processing: remove special characters
    '''
    chars = re.escape(string.punctuation)
    clean = [re.sub(r'['+chars+']', '',my_str) for my_str in cols]
    clean = [i.lower().replace(' ','_') for i in clean]
    clean = ['product_code_sku' if 'product_code' in i else i for i in clean]
    return clean

def most_recent_product_file():
    '''most_recent_product_file docstring'''
    path = '.'
    files = list_files_in_directory(path)
    x = [i for i in files if 'products-' in i]
    x.sort()
    filepath = x[-1]
    # print(filepath)
    return filepath