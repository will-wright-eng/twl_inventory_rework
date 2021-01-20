import pandas as pd
import numpy as np
import re


def vendor_label(element):
    '''docstring for vendor_label'''
    element = element.upper()
    if 'INNOVA' in element:
        #print(element)
        vendor = 'INNOVA'
    elif 'WHAM' in element:
        #print(element)
        vendor = 'WHAM-O'
    elif 'DISCRAFT' in element:
        vendor = 'DISCRAFT'
    elif 'DISCMANIA' in element:
        vendor = 'DISCMANIA'
    else:
        vendor = np.nan
    return vendor


def plastic_label(element):
    '''docstring for plastic_label'''
    element = element.upper()
    # excluding GLO because I'm going to use this to select golf discs and ultra-stars have GLO
    plastics = [
        "Z FLX", " Z ", "Z-LINE", "Z LINE", " D ", "D LINE", "D-LINE",
        "X-LINE", "X LINE", "FLX", "ESP", "SS", "OOP", "ELITE", " X "
    ]  #, "GLO"]
    p = []
    for x in plastics:
        if x in element:
            p.append(x)
    if len(p) >= 1:
        p = ','.join(p)
        return p
    else:
        return np.nan


def model_label(element):
    '''docstring for model_label'''
    models = ["SKY-STYLER", "ULTRA-STAR", "ULTRA STAR", "ULTRASTAR", "GOLF"]
    element = element.upper()
    label = ''
    for model in models:
        if model in element:
            label = model
            break
    if len(label) > 1:
        if 'ULTRA' in label:
            return "ULTRA-STAR"
        else:
            return label
    else:
        return np.nan


def find_year(element):
    '''docstring for find_year'''
    pattern = '([0-9][0-9][0-9][0-9])'
    m = re.findall(pattern, element)
    if len(m) >= 1:
        return m[0]
    else:
        return np.nan


def remove_labels(element, vendor, plastic):
    '''docstring for remove_labels'''
    ele = element.upper()
    try:
        if len(vendor) > 0:
            ele = ele.replace(vendor, '')
        try:
            if len(plastic) > 0:
                for x in plastic.split(','):
                    ele = ele.replace(x, '')
        except TypeError:
            pass
    except TypeError:
        pass
    return ele.strip().replace('  ', ' ').replace('(', '').replace(')', '')


def set_len_col(df):
    '''docstring for set_len_col'''
    x = []
    for col in df.columns:
        l = set(df[col])
        if len(l) < 10:
            x.append([col, len(l), l])
        else:
            x.append([col, len(l), {}])
    temp = pd.DataFrame(x)
    temp.columns = ['index', 'set_length', 'set_values']
    temp = temp.set_index('index')
    return temp


def join_into_to_stats_table(stats_table):
    '''docstring for'''
    d_info = pd.read_csv('./bigcommerce/bc_import_fields.csv')
    d_info.columns = [
        i.lower().replace(' / ', '_').replace(' ', '_') for i in d_info.columns
    ]
    col = 'field'
    d_info[col] = [
        i.lower().replace(' ', '_').replace('+', '').replace('/', '').replace(
            '?', '').replace('-', '').replace('__', '_') for i in d_info[col]
    ]
    stats_table.reset_index(drop=False, inplace=True)
    ndf = stats_table.merge(d_info,
                            how='left',
                            left_on='index',
                            right_on='field')
    return ndf


def split_category(element, n):
    '''docstring for'''
    try:
        x = element.split('/')
        if 'Template' in x[n]:
            return 'Template'
        return x[n]
    except IndexError:
        return np.nan


def label_categories(element):
    '''docstring for'''
    include = ['Disc Golf', 'Freestyle Frisbee', 'Ultimate Frisbee']
    flag = False
    for word in include:
        if word in element:
            flag = True
    return flag


def process_csv_step_one(df):
    '''docstring for process_csv_step_one
    remove rows with null elements in product_name and category
    removes non-discraft product rows
    
    input: product dataframe
    output: additional columns
    '''
    df.product_name = ['null' if pd.isnull(i) else i for i in df.product_name]
    df.category = ['null' if pd.isnull(i) else i for i in df.category]
    fxns = [vendor_label, plastic_label, model_label, find_year]
    new_cols = ['label_vendor', 'label_plastic', 'label_model', 'label_year']
    for fxn, col in zip(fxns, new_cols):
        df[col] = df['product_name'].apply(lambda x: fxn(x))
    df['product_name_mod'] = df.apply(lambda x: remove_labels(
        x['product_name'], x['label_vendor'], x['label_plastic']),
                                      axis=1)
    ###
    df = df.loc[df['label_vendor'] != 'INNOVA']
    df = df.loc[df['label_vendor'] != 'WHAM-O']
    df = df.loc[df['label_vendor'] != 'DISCMANIA']

    df = df.reset_index(drop=True)
    return df


def process_csv_step_two(df):
    '''docstring for process_csv_step_two
    input: table of products and skus for all brands
    output: filtered table
    
    attributes
        - discraft products
        - only relevant categories based on categorie 0 split
        - only visible products
    '''
    df = df.loc[df.brand_name == 'Discraft Products']
    df = df.loc[pd.isnull(df.category) == False]
    for n in range(5):
        df['category_' +
           str(n)] = df.category.apply(lambda x: split_category(x, n))
    df['category_flag'] = df.category_0.apply(lambda x: label_categories(x))
    df = df.loc[df['category_flag']]
    df = df.loc[df['product_visible'] == 'Y']
    return df


def reduced_table(df):
    '''docstring for'''
    # reduce rows
    ndf = df.loc[df.category_flag]
    # recude columns
    d, cols = df_stats(df)
    ndf = ndf[cols]
    return ndf


def join_bulk_import_label(stats_table, file_list):
    '''docstring for join_bulk_import_label'''
    file = 'bulk-edit-product-import-template.csv'
    filename = [i for i in file_list if file in i][0]
    df = pd.DataFrame(clean_cols(list(pd.read_csv(filename))))
    df['for import'] = 'bulk import'
    df.columns = ['cols', 'for_import']
    ndf = stats_table.merge(df, how='left', left_on='index', right_on='cols')
    return ndf
