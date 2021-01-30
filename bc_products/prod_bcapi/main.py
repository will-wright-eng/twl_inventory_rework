'''
main script for executing product modifications
    via BigCommerce API

Product endpoint: 
    https://developer.bigcommerce.com/api-reference/
        store-management/catalog/products/getproductbyid

Author: William Wright
'''

import os
import re
import sys
import inspect
import logging

import numpy as np
import pandas as pd

from PIL import Image
import imgkit

import boto3
import progressbar

from modules.clean_description import clean_description
from modules.util_fxns import util_fxns as utilf

program_name = 'prod_bcapi'

regex_dict = {
    '<h3>FLIGHT CHARACTERISTICS</h3>.+?</a></p>':
    '',
    '<p>Information about <a title="Information about this plastic type.+?</p>':
    '',
    '<h3>More Information</h3> <p>.+':
    '',
    '<h3>SPECIFICATIONS</h3>.+?<li>Best':
    '<h3>SPECIFICATIONS</h3> <ul> <li>Best',
    'Check out how it flies here.</p> <p><!-- mceItemMediaService.+?mceItemMediaService --></p>':
    ''
}

config = configparser.ConfigParser()
config.read('../project.cfg')
cfg_dict = dict(config.items(program_name))
imgs_bool = cfg_dict['imgs_bool']

logger = function_logger(logging.DEBUG,
                               logging.DEBUG,
                               function_name=program_name)

def gen_preview_image(old_html, new_html, base_name, output_folder_results,
                      output_folder_html):
    '''docstring for gen_preview_image'''
    image_names = [
        output_folder_html + '/' + base_name + '_old.png',
        output_folder_html + '/' + base_name + '_new.png'
    ]
    
    imgkit.from_string(old_html, image_names[0])
    imgkit.from_string(new_html, image_names[1])

    images = [Image.open(x) for x in image_names]
    widths, heights = zip(*(i.size for i in images))
    total_width = max(widths)
    max_height = sum(heights) + 10
    new_im = Image.new('RGB', (total_width, max_height))
    offset = 0
    for im in images:
        new_im.paste(im, (0, offset))
        offset += im.size[1] + 10
    
    new_im.save(output_folder_results + '/' + base_name + '.png')


def check_batch_overlap(prod_ids_filepath, batch_prod_ids):
    '''check_batch_overlap docstring'''
    folder = '../tables/'
    files = [i for i in os.listdir(folder) if 'products-20' in i]
    exclude_batch = prod_ids_filepath.split('/')[-1]
    files = [i for i in files if i != exclude_batch]
    prod_ids = []
    for file in files:
        df = pd.read_csv(folder + file)
        df = df.loc[df['Product Type'] == 'P']
        prod_id = list(df['Product ID'])
        prod_ids.append(prod_id)
    ids = [int(j) for i in prod_ids for j in i]
    res = []
    for prod_id in batch_prod_ids:
        prod_id = int(prod_id)
        if prod_id in ids:
            logger.warn('WARNING: overlapping id found: ' + str(prod_id))
            res.append(prod_id)
    return res


def run_process(df, prod_ids, output_folder_results, output_folder_html,
                folder_name):
    '''run_process docstring'''
    res = {}
    logger.info('run')
    for _id in prod_ids:
        logger.info('processing: ' + str(_id))
        temp = df.loc[df.product_id == _id]
        if len(temp) > 0:
            _name = process_cols_v2(temp.product_name)[0]
            _sku = str(temp.product_code_sku.values[0])
            _cateogry = str(temp.category.values[0])
            base_name = str(_id) + '_' + _name + '_' + _sku
            old_html = temp.product_description.values[0]
            if isinstance(old_html, str):
                desc = clean_description(old_html, regex_dict, logger)
                d = desc.flight_chars_dict()
                new_html = desc.clean()
                _data = [
                    temp.product_name.values[0], _sku, _cateogry, base_name,
                    old_html, new_html,
                    len(re.findall('please note', new_html.lower())),
                    len(re.findall('flight characteristics',
                                   new_html.lower())),
                    len(re.findall('information about', new_html.lower()))
                ]
                _data_cols = [
                    'id', 'name', 'sku', 'category', 'base_name', 'old_html',
                    'new_html', 'count_please_note', 'count_flight_chars',
                    'count_info_about'
                ]
                if len(d) == 4:
                    res[_id] = _data + [d[i] for i in d]
                    flight_char_cols = [i for i in d]
                else:
                    res[_id] = _data + [np.nan] * 4

                if imgs_bool:
                    try:
                        # videos incompatible with command line tool
                        old_html = re.sub(
                            '<p><!-- mceItemMediaService.+?mceItemMediaService --></p>',
                            '', old_html)
                        gen_preview_image(old_html, new_html, base_name,
                                          output_folder_results,
                                          output_folder_html)
                    except OSError as e:
                        logger.error('OSError: ' + str(e))
            else:
                logger.info(base_name + ' skipped')
        else:
            logger.info(str(_id) + ' --> no match found')
    df = pd.DataFrame(res).T
    df.reset_index(inplace=True)
    df.columns = _data_cols + flight_char_cols
    df['href_check'] = df.new_html.apply(lambda x: 'href' in x)
    return df


def main():
    '''main docstring'''
    
    logger.info('-- NEW JOB --')
    
    # load product id list
        # loop through list of csvs if len(x) > 1
        prod_ids = list(product_df(prod_ids_filepath).product_id)

    logger.info(prod_ids_filepath)
    
    overlap_list = check_batch_overlap(prod_ids_filepath, prod_ids)
    if len(overlap_list) > 0:
        logger.info('overlapping = ' + str(overlap_list))

    prod_ids = [i for i in prod_ids if i not in overlap_list]
    folder_name = prod_ids_filepath.split('/')[-1].replace('.csv', '')

    # load product info via API call

    folders = [
        'results', 'results/' + folder_name,
        'results/' + folder_name + '/' + output_folder_results,
        'results/' + folder_name + '/' + output_folder_html
    ]
    
    utilf.create_directory(folders, logger)
    
    logger.info('start')

    df = run_process(df, prod_ids, output_folder_results,
                    output_folder_html, folder_name)

    # save csv
    # df.to_csv(folder_name + '.csv', index=False)

    # zip combined images and csv

    # upload to s3
    utilf.upload_to_s3(path_output, bucket_name, key_path, logger)
    logger.info(folder_name + ' saved to S3')
    logger.info('done')

    # loop through product ids and update with new_html

if __name__ == '__main__':
    main()
