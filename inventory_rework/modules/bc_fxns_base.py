import pandas as pd
import numpy as np
from .utility_fxns import distribute


def generate_id_dict(id_list, prod_ids, df):
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
            step = pos + j
            if (df.item_type[step] == 'Product') & (j == 1):
                j = 0
                flag = False
            elif df.item_type[step] == 'Product':
                j -= 1
                flag = False
            elif df.item_type[step] == 'SKU':
                j += 1
                sku_ids.append(df.product_id[step])
            else:
                # not a product or sku
                j = 0
                flag = False
        id_dict[i] = [pos, j, sku_ids]
    return id_dict


def sku_combo_dicts_v2(file_list):
    '''docstring for sku_combo_dicts'''
    file = 'color_table.csv'
    filename = [i for i in file_list if file in i][0]
    df = pd.read_csv(filename)
    cols = ['dg', 'uf', 'ff']
    color_dicts = {}
    for col in cols:
        ndf = df.loc[df[col] == True]
        color_dicts[col + '_color_dict'] = {
            i: [j, k]
            for (i, j, k) in zip(range(len(ndf)), ndf.color, ndf.new_code)
        }
    file = 'weight_table.csv'
    filename = [i for i in file_list if file in i][0]
    df = pd.read_csv(filename)
    ndf = df.loc[df.dg1 == True]
    weight_dict = {
        i: [j, k]
        for (i, j, k) in zip(range(len(ndf)), ndf.weights, ndf.codes)
    }
    return color_dicts, weight_dict


def generate_sku_info_v2(master_sku, mfg_code, color_dicts, weight_dict,
                         category):
    '''docstring for generate_sku_info
    input: master sku and the sku combination
    output: list of sku ids for each sku combination
        return_flag condition triggered if category != defined categories'''
    return_flag = True
    if (category == 'Disc Golf') or (category == 'Disc Golf - Stock Models'):
        dg_color_dict = color_dicts['dg_color_dict']
        sku_names = [
            '[S]Disc color=' + dg_color_dict[i][0] + ',[S]Disc weight=' +
            weight_dict[j][0] for i in range(len(dg_color_dict))
            for j in range(len(weight_dict))
        ]
        sku_codes = [
            dg_color_dict[i][1] + str(weight_dict[j][1])
            for i in range(len(dg_color_dict)) for j in range(len(weight_dict))
        ]
    elif category == 'Ultimate Frisbee':
        uf_color_dict = color_dicts['uf_color_dict']
        sku_names = [
            '[S]Disc color=' + uf_color_dict[i][0]
            for i in range(len(uf_color_dict))
        ]
        sku_codes = [uf_color_dict[i][1] for i in range(len(uf_color_dict))]
    elif (category == 'Freestyle Frisbee') or (
            category == 'Sky-Styler Color Options'):
        ff_color_dict = color_dicts['ff_color_dict']
        sku_names = [
            '[S]Disc color=' + ff_color_dict[i][0]
            for i in range(len(ff_color_dict))
        ]
        sku_codes = [ff_color_dict[i][1] for i in range(len(ff_color_dict))]
    else:
        return_flag = False
        return None, None, return_flag
    sku_codes = [master_sku + mfg_code + code for code in sku_codes]
    return sku_names, sku_codes, return_flag


def sku_struct_v2(master_sku, mfg_code, sku_ids, stock_total, category,
                  color_dicts, weight_dict, stock_field, index_by):
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
    sku_names, sku_codes, return_flag = generate_sku_info_v2(
        master_sku, mfg_code, color_dicts, weight_dict, category)

    if return_flag:
        if (len(sku_ids) < len(sku_codes)):
            sku_ids = sku_ids + [''] * (len(sku_codes) - len(sku_ids))
        stock_values = distribute(stock_total, len(sku_codes))
        for pid, psku, pname, stock in zip(sku_ids, sku_codes, sku_names,
                                           stock_values):
            row = [item, pid, psku, pname, cost, stock, stock_low, ship]
            rows.append(row)
        cols = [
            'item_type', 'product_id', index_by, 'product_name', 'cost_price',
            stock_field, 'low_stock_level', 'free_shipping'
        ]
        df = pd.DataFrame(rows)
        df.columns = cols
        return df, return_flag
    else:
        return None, return_flag


def clean_products_df(df):
    '''docstring for clean_products_df
    input: dataframe of Product item_types
    output: clean select columns'''
    df.low_stock_level = 5
    df.price = df.price.fillna(value=0)
    df.price = df.price.astype(float)
    df.sale_price = round(df.price * 0.75, 2)
    df.track_inventory = 'by option'
    df.product_condition = 'New'
    #df.option_set = 'inventory_rework_v0.9.1'
    df.product_name = [i.title() for i in df.product_name]
    return df


def product_option_set(row_prod, category):
    '''docstring for product_option_set
    apply option set name specific to variance category'''
    option_set_base = 'inventory_rework_v0.9.1'
    if (category == 'Disc Golf') or (category == 'Disc Golf - Stock Models'):
        row_prod.loc['option_set'] = option_set_base + '_dg'
    elif category == 'Ultimate Frisbee':
        row_prod.loc['option_set'] = option_set_base + '_uf'
    elif (category == 'Freestyle Frisbee') or (
            category == 'Sky-Styler Color Options'):
        row_prod.loc['option_set'] = option_set_base + '_ff'
    else:
        row_prod.loc['option_set'] = option_set_base + '_'
        print(
            'WARNING: no valid category, return_flag should have been raised in sku_struct_v2'
        )
    return row_prod
