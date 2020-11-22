'''
Author: William Wright

Cleans product descriptions formatting in html, based off of standard patterns. Edge cases to be evaluated separately. 

# test metrics
    # percent of content removed
    # re.find_all --> number of matching patterns
    # bool for flight characteristics image
    # bake tests into 
'''

%reset -f

import pandas as pd
import re

import imgkit
import sys
from PIL import Image

from my_utils import list_files_in_directory, process_cols_v2
from my_configs import prod_ids_filepath, prod_ids_test_filepath, product_export_file, output_folder_html, output_folder_results
import clean_description

pd.set_option('display.max_columns', 500)
pd.set_option('display.max_rows', 500)

def product_df(filepath):
    '''product_df docstring
    return most recent product export from bigcommerce'''
    df = pd.read_csv(filepath)
    df.columns = process_cols_v2(df.columns)
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

def most_recent_product_file():
    '''most_recent_product_file docstring'''
    path = '.'
    files = list_files_in_directory(path)
    x = [i for i in files if 'products-' in i]
    x.sort()
    filepath = x[-1]
    print(filepath)
    return filepath

def run_process(df,prod_ids,output_folder_results,output_folder_html):
    '''run_process docstring'''
    for _id in prod_ids:
        temp = df.loc[df.product_id==_id]
        _name = process_cols_v2(temp.product_name)[0]
        _sku = temp.product_code_sku.values[0]
        base_name = _name+'_'+_sku
        print('\n\n',base_name)
        old_html = temp.product_description.values[0]
        new_html = clean_description(old_html).clean()
        #print(old_html, '\n\n','-'*10,'\n\n',new_html)
        
        try:
            # videos incompatible with command line tool
            old_html = re.sub('Check out how it flies here.</p> <p><!-- mceItemMediaService.+?mceItemMediaService --></p>','',old_html)
            gen_preview_image(old_html,new_html,base_name,output_folder_results,output_folder_html)
        except OSError as e:
            print('\n\n',base_name)
            print(e)
            
def main():
    '''main docstring'''
    if product_export_file == 'most recent':
        filepath = most_recent_product_file()
    else:
        filepath = '../systems/bigcommerce/data_imports/products-2020-11-10.csv'
    df = product_df(filepath)

    test = False
    if test:
        prod_ids = list(pd.read_csv(prod_ids_test_filepath).product_id) # testset    
    else:
        prod_ids = list(product_df(prod_ids_filepath).product_id) # disc golf set 01

    run_process(df,prod_ids,output_folder_results,output_folder_html)


if __name__ == '__main__':
    main()