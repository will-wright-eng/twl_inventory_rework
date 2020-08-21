import pandas as pd
import numpy as np
from utility_fxns import distribute,process_cols_v2,gen_cols_dict

def sku_combo_dicts_v2(file_list):
    '''docstring for sku_combo_dicts'''
    file = 'color_table.csv'
    filename = [i for i in file_list if file in i][0]
    df = pd.read_csv(filename)
    cols = ['dg','uf','ff']
    color_dicts = {}
    for col in cols:
        ndf = df.loc[df[col]==True]
        color_dicts[col+'_color_dict'] = {i:[j,k] for (i,j,k) in zip(range(len(ndf)),ndf.color,ndf.new_code)}
    file = 'weight_table.csv'
    filename = [i for i in file_list if file in i][0]
    df = pd.read_csv(filename)
    ndf = df.loc[df.dg1==True]
    weight_dict = {i:[j,k] for (i,j,k) in zip(range(len(ndf)),ndf.weights,ndf.codes)}
    return color_dicts, weight_dict

def import_template_cols():
    filename = [i for i in file_list if 'InventoryImportSample.csv' in i][0]
    df = pd.read_csv(filename)
    import_cols = process_cols_v2(list(df))
    return import_cols

def extract_and_dict(file_list):
    # extract sku list from processed bigcommerce product table
    file = 'master_list_discraft_skus.csv'
    filename = [i for i in file_list if file in i][0]
    df0 = pd.read_csv(filename)
    prod_ids = list(df0.product_code_sku)
    # lightspeed inventory
    file = '2020-08-17_item_listings_local_matches.csv'
    filename = [i for i in file_list if file in i][0]
    df1 = pd.read_csv(filename)
    cols = list(df1)
    clean_cols = process_cols_v2(df1.columns)
    df1.columns = clean_cols
    cols_dict = gen_cols_dict(cols,clean_cols)
    # create id dictionary
    temp1 = [list(df1.custom_sku).index(i) for i in prod_ids if i in list(df1.custom_sku)]
    temp2 = [i for i in prod_ids if i in list(df1.custom_sku)]
    categories = [list(df0.loc[df0.product_code_sku==i].category_0)[0] for i in temp2]
    id_dict = {i:[j,k] for (i,j,k) in zip(temp2, temp1,categories)}
    df = df1.iloc[temp1]
    return df,id_dict,cols_dict

def gen_prod_matrix(df,id_dict,mfg_code,prod,color_dicts,weight_dict):
    category = id_dict[prod][1]
    row = df.loc[df.custom_sku == prod]
    sys_id = row.system_id.values[0]
    upc = row.upc.values[0]
    stock = int(row.qty)
    master_sku = row.custom_sku.values[0]
    matrix_desc = row.item.values[0].title()
    return_flag=True
    if category=='Disc Golf':
        matrix_set = 'Color/Weight'
        mcols = ['attribute_1','attribute_2']
        dg_color_dict = color_dicts['dg_color_dict']
        attributes = [[dg_color_dict[i][0],weight_dict[j][0]] for i in range(len(dg_color_dict)) for j in range(len(weight_dict))]
        sku_codes = [dg_color_dict[i][1]+str(weight_dict[j][1]) for i in range(len(dg_color_dict)) for j in range(len(weight_dict))]
    elif (category == 'Freestyle Frisbee') or (category == 'Sky-Styler Color Options') or (category == 'Ultimate Frisbee'):
        matrix_set = 'Color'
        mcols = ['attribute_1']
        uf_color_dict = color_dicts['uf_color_dict']
        attributes = [[uf_color_dict[i][0]] for i in range(len(uf_color_dict))]
        sku_codes = [uf_color_dict[i][1] for i in range(len(uf_color_dict))]
    else:
        return_flag=False
    sku_codes = [master_sku+mfg_code+code for code in sku_codes]
    temp = pd.DataFrame(attributes)
    temp.columns = mcols
    row = row.append([row]*(len(temp)-1),ignore_index=True)
    matrix = pd.concat([row,temp],axis=1)
    matrix.system_id = np.nan
    matrix.system_id[0] = sys_id
    matrix.upc = np.nan
    matrix.upc[0] = upc
    qty_col = distribute(int(stock),len(matrix))
    matrix.qty = qty_col
    matrix['matrix_attribute_set'] = matrix_set
    matrix['matrix_description'] = matrix_desc
    if return_flag:
        if len(mcols)==1:
            matrix['description'] = matrix['matrix_description']+' ('+matrix['attribute_1']+')'
        elif len(mcols)==2:
            matrix['description'] = matrix['matrix_description']+' ('+matrix['attribute_1']+' '+matrix['attribute_2']+')'
    matrix.custom_sku = sku_codes
    return return_flag,matrix