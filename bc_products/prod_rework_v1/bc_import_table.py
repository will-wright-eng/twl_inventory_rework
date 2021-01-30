'''
Created by William Wright on 2020-08-25.
Copyright © 2020 William Wright. All rights reserved.
'''

import pandas as pd
import os
import datetime as dt

today = str(dt.datetime.today()).split(' ')[0]
bc_product_export = os.environ["bc_product_export"]
ls_product_export = os.environ["ls_product_export"]
master_sku_file = os.environ["master_sku_file"]

from modules.utility_fxns import list_files_in_directory, process_cols_v2, gen_cols_dict
from modules.bc_fxns_core import full_inventory_df_info, gen_prod_id_dict, gen_import_table_with_skus_v2
# from modules.bc_fxns_base import sku_combo_dicts


def main():
    # # command line arguments
    file_list = list_files_in_directory('.')
    filename1 = [i for i in file_list if master_sku_file in i][0]
    filename2 = [i for i in file_list if bc_product_export in i][0]
    # extract info from cleaned bigcommerce product table
    category_col = 'category_0'
    index_by = 'product_code_sku'
    stock_field = 'current_stock_level'
    test = False
    prod_ids = gen_prod_id_dict(filename1, index_by, category_col, test)
    # load full bigcommerce inventory and index prod_ids with sku count and sku prod ids
    df, id_list, id_dict, df, cols_dict = full_inventory_df_info(
        filename2, index_by, prod_ids)
    # loop through discraft product list and pull sequence of skus under each product in list
    mfg_code = 'DIS'
    ndf = gen_import_table_with_skus_v2(df, prod_ids, id_dict, index_by,
                                        stock_field, mfg_code, file_list)
    ndf.columns = [cols_dict[i] for i in ndf.columns]
    file = '/data_imports/' + today + '_bc_import_table.csv'
    filename3 = '/'.join(filename2.split('/')[:-2]) + file
    ndf.to_csv(filename3, index=False)


if __name__ == '__main__':
    main()
