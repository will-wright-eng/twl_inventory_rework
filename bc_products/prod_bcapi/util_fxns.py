'''
utility functions for general use
Author: William Wright
'''

import os
import string
import inspect
import logging

def process_cols(cols):
    '''docstring for process_cols
    for processing: remove special characters
    '''
    chars = re.escape(string.punctuation)
    clean = [re.sub(r'[' + chars + ']', '', my_str) for my_str in cols]
    clean = [i.lower().replace(' ', '_') for i in clean]
    clean = ['product_code_sku' if 'product_code' in i else i for i in clean]
    return clean

def product_df(filepath):
    '''product_df docstring
    return most recent product export from bigcommerce'''
    df = pd.read_csv(filepath)
    df.columns = process_cols_v2(df.columns)
    df = df.loc[df.item_type == 'Product']
    return df

def files_in_directory(path):
    '''docstring for list_files_in_directory'''
    file_list = []
    cwd = os.getcwd()
    for root, dirs, files in os.walk('.' + path):
        for file in files:
            file_list.append(root + '/' + file)
    return file_list

def most_recent_product_file():
    '''most_recent_product_file docstring'''
    path = '.'
    files = list_files_in_directory(path)
    x = [i for i in files if 'products-' in i]
    x.sort()
    filepath = x[-1]
    return filepath

def create_directory(folders, logger=None):
    '''create_directory docstring'''
    for folder in folders:
        try:
            os.mkdir(folder)
        except FileExistsError as e:
            if logger:
                logger.info(e)
            else:
                print(e)

def function_logger(file_level, console_level=None, function_name=None):
    '''function_logger docstring'''
    if function_name == None:
        function_name = inspect.stack()[1][3]
    logger = logging.getLogger(function_name)
    logger.setLevel(logging.DEBUG)  #By default, logs all messages

    if console_level != None:
        ch = logging.StreamHandler()  #StreamHandler logs to console
        ch.setLevel(console_level)
        ch_format = logging.Formatter('%(asctime)s - %(message)s')
        ch.setFormatter(ch_format)
        logger.addHandler(ch)

    fh = logging.FileHandler("{0}.log".format(function_name))
    fh.setLevel(file_level)
    fh_format = logging.Formatter(
        '%(asctime)s - %(lineno)d - %(levelname)-8s - %(message)s')
    fh.setFormatter(fh_format)
    logger.addHandler(fh)
    return logger

def upload_to_s3(path_output, bucket_name, key_path, logger=None):
    '''upload_to_s3 docstring'''
    file_name = path_output.split('/')[-1]
    object_name = key_path + '/' + file_name
    s3 = boto3.client('s3')
    statinfo = os.stat(path_output)
    if logger:
        logger.info('uploading file:\t' + file_name)
        logger.info('uploading destination:\t' + object_name)

    up_progress = progressbar.progressbar.ProgressBar(maxval=statinfo.st_size)
    up_progress.start()

    def upload_progress(chunk):
        up_progress.update(up_progress.currval + chunk)

    s3.upload_file(path_output,
                   bucket_name,
                   object_name,
                   Callback=upload_progress)
    up_progress.finish()
    logger.info('upload complete')
