import pandas as pd
from utility_fxns import process_cols,gen_cols_dict
from bc_fxns_base import generate_id_dict,sku_combo_dicts,sku_struct,clean_products_df,sku_combo_dicts_v2,sku_struct_v2

def pull_list_of_prods(filename,index_by,category_col):
    '''import discraft product table for list of product IDs and their associated product category
    output: dictionary of product ids and their respective category'''
    df = pd.read_csv(filename)
    prod_ids = pd.Series(df[category_col].values,index=df[index_by].values).to_dict()
    return prod_ids

def full_inventory_df_info(filename,index_by,prod_ids):
    '''docstring for full_inventory_df_info'''
    df = pd.read_csv(filename)
    cols = list(df)
    clean_cols = process_cols(df.columns)
    cols_dict = gen_cols_dict(cols,clean_cols)
    df.columns = clean_cols
    df.item_type = df.item_type.apply(lambda x: x.strip())
    id_list = list(df[index_by])
    id_dict = generate_id_dict(id_list,list(prod_ids),df)
    return df, id_list, id_dict, df, cols_dict

def gen_prod_id_dict(filename,index_by,category_col,test):
    if test:
        test_skus = ['1550','1707','5197']
        test_sku_categories = ['Disc Golf','Ultimate Frisbee','Freestyle Frisbee']
        prod_ids = pd.Series(test_sku_categories,index=test_skus).to_dict()
    else:
        prod_ids = pull_list_of_prods(filename,index_by,category_col)
    return prod_ids

def keep_nonempty_cols(df):
    '''docstring for keep_nonempty_cols'''
    temp = pd.DataFrame(df.count())
    temp.reset_index(inplace=True,drop=False)
    temp.columns = ['cols','value_count']
    temp = temp.loc[temp['value_count']!=0]
    keep_cols = list(temp.cols)
    return keep_cols

def gen_import_table_with_skus(df, prod_ids, id_dict, index_by, stock_field, mfg_code):
    '''docstring for gen_import_table_with_skus'''
    products = []
    skus = []
    dg_color_dict,dg_weight_dict = sku_combo_dicts()
    for prod in list(prod_ids):
        # pull product row
        row_prod = df.iloc[id_dict[prod][0]]
        master_sku = row_prod[index_by]
        stock_total = row_prod[stock_field]
        sku_ids = id_dict[prod][2]
        category = prod_ids[prod]
        # generate product skus
        rows_sku, return_flag = sku_struct(master_sku,mfg_code,sku_ids,stock_total,category,dg_color_dict,dg_weight_dict,stock_field,index_by)
        if return_flag:
            products.append(row_prod)
            skus.append(rows_sku)
        else:
            print(category)
    products = pd.concat(products,axis=1).T
    products = clean_products_df(products)
    skus = pd.concat(skus)
    ndf = pd.concat([products,skus])
    ndf.reset_index(drop=True,inplace=True)
    ndf = ndf[keep_nonempty_cols(ndf)]
    ndf.sort_values(by=[index_by,'item_type'],inplace=True)
    ndf.fillna(value='',inplace=True)
    return ndf

def gen_import_table_with_skus_v2(df,prod_ids,id_dict,index_by,stock_field,mfg_code):
    '''docstring for gen_import_table_with_skus'''
    products = []
    skus = []
    color_dicts,weight_dict = sku_combo_dicts_v2()
    for prod in list(prod_ids):
        # pull product row
        row_prod = df.iloc[id_dict[prod][0]]
        master_sku = row_prod[index_by]
        stock_total = row_prod[stock_field]
        sku_ids = id_dict[prod][2]
        category = prod_ids[prod]
        # generate product skus
        rows_sku, return_flag = sku_struct_v2(master_sku,mfg_code,sku_ids,stock_total,category,color_dicts,weight_dict,stock_field,index_by)
        if return_flag:
            products.append(row_prod)
            skus.append(rows_sku)
        else:
            print(category)
    products = pd.concat(products,axis=1).T
    products = clean_products_df(products)
    skus = pd.concat(skus)
    ndf = pd.concat([products,skus])
    ndf.reset_index(drop=True,inplace=True)
    ndf = ndf[keep_nonempty_cols(ndf)]
    ndf.sort_values(by=[index_by,'item_type'],inplace=True)
    ndf.fillna(value='',inplace=True)
    return ndf