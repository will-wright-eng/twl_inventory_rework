'''
Author: William Wright

Cleans product descriptions formatting in html, based off of standard patterns. 
Edge cases to be evaluated separately. 
'''

import re
import os

import numpy as np
import pandas as pd
import imgkit
import sys
from PIL import Image

import logging
import inspect
import configparser

import modules.util_fxns as utilf
from modules.regex_dict import regex_dict
from modules.clean_description import clean_description

config = configparser.ConfigParser()
config.read('../project.cfg')
cfg_dict = dict(config.items('desc_cleanup'))

product_export_file = cfg_dict['product_export_filepath']+cfg_dict['product_export_file']
prod_ids_filepaths = [cfg_dict['prod_ids_filepaths']]
imgs_bool = cfg_dict['imgs_bool']
output_folder_html = cfg_dict['output_folder_html']
output_folder_results = cfg_dict['output_folder_results']
program_name = cfg_dict['program_name']


logger = utilf.function_logger(logging.DEBUG,
                               logging.DEBUG,
                               function_name= program_name)

def product_df(filepath):
    '''product_df docstring
    return most recent product export from bigcommerce'''
    df = pd.read_csv(filepath)
    df.columns = utilf.process_cols_v2(df.columns)
    df = df.loc[df.item_type == 'Product']
    return df

def gen_preview_image(old_html,new_html,base_name,output_folder_results,output_folder_html):
    '''docstring for gen_preview_image'''
    image_names = [output_folder_html+'/'+base_name+'_old.png', output_folder_html+'/'+base_name+'_new.png']
    imgkit.from_string(old_html, image_names[0])
    imgkit.from_string(new_html, image_names[1])
    images = [Image.open(x) for x in image_names]
    widths, heights = zip(*(i.size for i in images))
    total_width = max(widths)
    max_height = sum(heights) + 10
    new_im = Image.new('RGB', (total_width, max_height))
    offset = 0
    for im in images:
        new_im.paste(im, (0,offset))
        offset += im.size[1]+ 10
    new_im.save(output_folder_results+'/'+base_name+'.png')

def run_process(df,prod_ids,output_folder_results,output_folder_html,folder_name):
    '''run_process docstring'''
    res = {}
    logger.info('run')
    for _id in prod_ids:
        logger.info('processing: '+str(_id))
        temp = df.loc[df.product_id == _id]
        if len(temp)>0:
            _name = utilf.process_cols_v2(temp.product_name)[0]
            _sku = str(temp.product_code_sku.values[0])
            _cateogry = str(temp.category.values[0])
            base_name = str(_id)+'_'+_name+'_'+_sku
            old_html = temp.product_description.values[0]
            if isinstance(old_html,str):
                desc = clean_description(old_html, regex_dict, logger)
                d = desc.flight_chars_dict()
                new_html = desc.clean()
                _data = [temp.product_name.values[0],_sku,_cateogry,base_name,old_html,new_html,
                    len(re.findall('please note',new_html.lower())),
                    len(re.findall('flight characteristics',new_html.lower())),
                    len(re.findall('information about',new_html.lower()))
                    ]
                _data_cols = ['id','name','sku','category','base_name','old_html','new_html','count_please_note',
                    'count_flight_chars','count_info_about'
                    ]
                if len(d)==4:
                    res[_id] = _data+[d[i] for i in d]
                    flight_char_cols = [i for i in d]
                else:
                    res[_id] = _data+[np.nan]*4
                
                if imgs_bool:
                    try:
                        # videos incompatible with command line tool
                        old_html = re.sub('<p><!-- mceItemMediaService.+?mceItemMediaService --></p>','',old_html)
                        gen_preview_image(old_html,new_html,base_name,output_folder_results,output_folder_html)
                    except OSError as e:
                        logger.error('OSError: '+str(e))
            else:
                logger.info(base_name+' skipped')
        else:
            logger.info(str(_id)+' --> no match found')
    df = pd.DataFrame(res).T
    df.reset_index(inplace=True)
    df.columns = _data_cols+flight_char_cols
    df['href_check'] = df.new_html.apply(lambda x: 'href' in x)
    df.to_csv(folder_name+'.csv',index=False)
    logger.info(folder_name+'.csv'+' saved')

def check_batch_overlap(prod_ids_filepath,batch_prod_ids):
    '''check_batch_overlap docstring'''
    folder = 'tables/'
    files = [i for i in os.listdir(folder) if 'products-20' in i]
    exclude_batch = prod_ids_filepath.split('/')[-1]
    files = [i for i in files if i != exclude_batch]
    prod_ids = []
    for file in files:
        df = pd.read_csv(folder+file)
        df = df.loc[df['Product Type']=='P']
        prod_id = list(df['Product ID'])
        prod_ids.append(prod_id)
    ids = [int(j) for i in prod_ids for j in i]
    res = []
    for prod_id in batch_prod_ids:
        prod_id = int(prod_id)
        if prod_id in ids:
            logger.warn('WARNING: overlapping id found: '+str(prod_id))
            res.append(prod_id)
    return res

def main():
    '''main docstring'''
    logger.info('-- NEW JOB --')
    df = product_df(product_export_file)
    for prod_ids_filepath in prod_ids_filepaths:
        logger.info(prod_ids_filepath)
        prod_ids = list(product_df(prod_ids_filepath).product_id)
        overlap_list = check_batch_overlap(prod_ids_filepath,prod_ids)
        if len(overlap_list)>0:
            logger.info('overlapping = '+ str(overlap_list))
        prod_ids = [i for i in prod_ids if i not in overlap_list]
        folder_name = prod_ids_filepath.split('/')[-1].replace('.csv','')
        folders = [
            'results',
            'results/'+folder_name,
            'results/'+folder_name+'/'+output_folder_results,
            'results/'+folder_name+'/'+output_folder_html
            ]
        utilf.create_directory(folders,logger)
        logger.info('start')
        try:
            cwd = os.getcwd()
            os.chdir(cwd+'/results/'+folder_name)
            run_process(df,prod_ids,output_folder_results,output_folder_html,folder_name)
            logger.info('done')
        finally:
            os.chdir(cwd)

if __name__ == '__main__':
    main()