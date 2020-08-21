import pandas as pd
import numpy as np
from utility_fxns import distribute

def sku_combo_dicts():
    '''docstring for sku_combo_dicts'''
    weights = [ '160-166 grams', '167-169 grams', '170-172 grams', '173-174 grams', '175-176 grams', '177-179 grams', '180 grams', '159 grams or less']
    wcodes = [ '6066', '6769', '7072', '7374', '7576', '7779', '8000', '5900']
    dg_weight_dict = {}
    for i,j,k in zip(range(len(weights)),weights,wcodes):
        dg_weight_dict[i]=[j,k]
    colors = [ 'Black', 'Blue', 'White', 'Green', 'Orange', 'Pink', 'Purple', 'Red', 'Yellow', 'Clear', 'Brown', 'Gray', 'Brown (dark)'
              , 'Brown (light)', 'Brownish swirly', 'Blue (dark)', 'Blue (light)', 'Bluish swirly', 'Blurple', 'Blurple-ish swirly', 'Gray (dark)'
              , 'Gray (light)', 'Grayish swirly', 'Green (dark)', 'Green (light)', 'Green (bright)', 'Greenish swirly', 'Orange (dark)', 'Orange (light)'
              , 'Orange (bright)', 'Orangish swirly', 'Pink (dark)', 'Pink (light)', 'Pink (bright)', 'Pinkish swirly', 'Purple (dark)', 'Purple (light)'
              , 'Purple (bright)', 'Purplish swirly', 'Red (dark)', 'Red (light)', 'Red (bright)', 'Reddish swirly', 'White (milky, clearish)'
              , 'Yellow (dark)', 'Yellow (light)', 'Yellow (bright)', 'Yellowish swirly']
    ccodes = [ 'BB', 'BL', 'WH', 'GN', 'OR', 'PK', 'PU', 'RE', 'YE', 'CL', 'BR', 'GR', 'DB', 'LB', 'BS', 'BD', 'BL', 'BU', 'BP', 'SB', 'DG', 'LG'
              , 'GS', 'GD', 'GL', 'BG', 'SG', 'DO', 'LO', 'BO', 'OS', 'DP', 'LP', 'BP', 'PS', 'PD', 'PL', 'PB', 'SP', 'DR', 'LR', 'BR', 'RS', 'WM'
              , 'DY', 'LY', 'BY', 'YS']
    dg_color_dict = {}
    for i,j,k in zip(range(len(colors)),colors,ccodes):
        dg_color_dict[i]=[j,k]
    return dg_color_dict, dg_weight_dict

def generate_sku_info(master_sku,mfg_code,dg_color_dict,dg_weight_dict,category):
    '''docstring for generate_sku_info
    input: master sku and the sku combination
        n: number of sequential weights
        m: number of sequential colors
    output: list of sku ids for each sku combination
        return_flag condition triggered if category != defined categories'''
    return_flag = True
    if (category == 'Disc Golf') or (category == 'Disc Golf - Stock Models'):
        n = 6 
        m = 12 
        sku_names = ['[S]Disc color='+dg_color_dict[i][0]+',[S]Disc weight='+dg_weight_dict[j][0] for i in range(m) for j in range(n)]
        # sku_codes = [dg_color_dict[i][1]+'_'+dg_weight_dict[j][1] for i in range(m) for j in range(n)]
        sku_codes = [dg_color_dict[i][1]+dg_weight_dict[j][1] for i in range(m) for j in range(n)]
    elif category == 'Ultimate Frisbee':
        m = 9 
        sku_names = ['[S]Disc color='+dg_color_dict[i][0] for i in range(m)]
        sku_codes = [dg_color_dict[i][1] for i in range(m)]
    elif (category == 'Freestyle Frisbee') or (category == 'Sky-Styler Color Options'):
        m = 9 
        sku_names = ['[S]Disc color='+dg_color_dict[i][0] for i in range(m)]
        sku_codes = [dg_color_dict[i][1] for i in range(m)]
    else:
        return_flag = False
        return None, None, return_flag
    # sku_codes = [master_sku+'_'+mfg_code+'_'+i for i in sku_codes]
    sku_codes = [master_sku+mfg_code+i for i in sku_codes]
    return sku_names, sku_codes, return_flag

def sku_struct(master_sku,mfg_code,sku_ids,stock_total,category,dg_color_dict,dg_weight_dict,stock_field,index_by):
    ''' docstring for sku_struct_disc_golf
    input: product sku and list of product IDs
    output: sku df to be appended to product row
    - generate product skus
    - apply standard sku structure as per product category
    '''
    rows = []
    item = 'SKU'
    cost = 0
    stock_low = 2
    ship = 'N'
    sku_names, sku_codes, return_flag = generate_sku_info(master_sku,mfg_code,dg_color_dict,dg_weight_dict,category)

    if return_flag:
        if (len(sku_ids)<len(sku_codes)):
            sku_ids = sku_ids + ['']*(len(sku_codes)-len(sku_ids))
        stock_values = distribute(stock_total, len(sku_codes))
        for pid,psku,pname,stock in zip(sku_ids,sku_codes,sku_names,stock_values):
            row = [item,pid,psku,pname,cost,stock,stock_low,ship]
            rows.append(row)
        cols = ['item_type','product_id',index_by,'product_name','cost_price',stock_field,'low_stock_level','free_shipping']
        df = pd.DataFrame(rows)
        df.columns = cols
        return df, return_flag
    else:
        return None, return_flag

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

def generate_sku_info_v2(master_sku,mfg_code,color_dicts,weight_dict,category):
    '''docstring for generate_sku_info
    input: master sku and the sku combination
    output: list of sku ids for each sku combination
        return_flag condition triggered if category != defined categories'''
    return_flag = True
    if (category == 'Disc Golf') or (category == 'Disc Golf - Stock Models'):
        dg_color_dict = color_dicts['dg_color_dict']
        sku_names = ['[S]Disc color='+dg_color_dict[i][0]+',[S]Disc weight='+weight_dict[j][0] for i in range(len(dg_color_dict)) for j in range(len(weight_dict))]
        sku_codes = [dg_color_dict[i][1]+weight_dict[j][1] for i in range(len(dg_color_dict)) for j in range(len(weight_dict))]
    elif category == 'Ultimate Frisbee':
        uf_color_dict = color_dicts['uf_color_dict']
        sku_names = ['[S]Disc color='+uf_color_dict[i][0] for i in range(len(uf_color_dict))]
        sku_codes = [uf_color_dict[i][1] for i in range(len(uf_color_dict))]
    elif (category == 'Freestyle Frisbee') or (category == 'Sky-Styler Color Options'):
        ff_color_dict = color_dicts['ff_color_dict']
        sku_names = ['[S]Disc color='+ff_color_dict[i][0] for i in range(len(ff_color_dict))]
        sku_codes = [ff_color_dict[i][1] for i in range(len(ff_color_dict))]
    else:
        return_flag = False
        return None, None, return_flag
    sku_codes = [master_sku+mfg_code+code for code in sku_codes]
    return sku_names, sku_codes, return_flag

def sku_struct_v2(master_sku,mfg_code,sku_ids,stock_total,category,color_dicts,weight_dict,stock_field,index_by):
    ''' docstring for sku_struct_disc_golf
    input: product sku and list of product IDs
    output: sku df to be appended to product row
    - generate product skus
    - apply standard sku structure as per product category
    '''
    rows = []
    item = 'SKU'
    cost = 0
    stock_low = 2
    ship = 'N'
    sku_names, sku_codes, return_flag = generate_sku_info(master_sku,mfg_code,color_dicts,weight_dict,category)

    if return_flag:
        if (len(sku_ids)<len(sku_codes)):
            sku_ids = sku_ids + ['']*(len(sku_codes)-len(sku_ids))
        stock_values = distribute(stock_total, len(sku_codes))
        for pid,psku,pname,stock in zip(sku_ids,sku_codes,sku_names,stock_values):
            row = [item,pid,psku,pname,cost,stock,stock_low,ship]
            rows.append(row)
        cols = ['item_type','product_id',index_by,'product_name','cost_price',stock_field,'low_stock_level','free_shipping']
        df = pd.DataFrame(rows)
        df.columns = cols
        return df, return_flag
    else:
        return None, return_flag

def generate_id_dict(id_list,prod_ids,df):
    ''' docstring for generate_id_dict
    input: product id list
    output: dictionary of
        key: product id
        values: [position of product id in full matrix
                , number of skus
                , sku product ids]'''
    id_dict = {}
    for i in prod_ids:
        pos = id_list.index(i)
        j = 1
        sku_ids = []
        flag = True
        while flag:
            step = pos+j
            if (df.item_type[step]=='Product')&(j==1):
                j = 0
                flag = False
            elif df.item_type[step]=='Product':
                j-=1
                flag = False
            elif df.item_type[step]=='SKU':
                j+=1
                sku_ids.append(df.product_id[step])
            else:
                # not a product or sku
                j = 0
                flag = False
        id_dict[i] = [pos,j,sku_ids]
    return id_dict

def clean_products_df(df):
    '''docstring for clean_products_df
    input: dataframe of Product item_types
    output: clean select columns'''
    df.low_stock_level = 5
    df.price = df.price.fillna(value=0)
    df.price = df.price.astype(float)
    df.sale_price = round(df.price*0.75,2)
    df.track_inventory = 'by option'
    df.product_condition = 'New'
    df.product_name = [i.title() for i in df.product_name]
    return df