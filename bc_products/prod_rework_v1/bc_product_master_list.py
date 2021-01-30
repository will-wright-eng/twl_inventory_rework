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

from modules.utility_fxns import list_files_in_directory, process_cols_v2, gen_cols_dict, distribute, cols_for_export
from modules.bc_fxns_preprocess import process_csv_step_one, process_csv_step_two


def main():
    #filename, bc_product_export, master_sku_file = sys.argv
    try:
        file_list = list_files_in_directory('.')
        filename = [i for i in file_list if bc_product_export in i][0]
    except indexError as e:
        print(e, '\n', 'file not found in directory')
    df = pd.read_csv(filename)
    cols = list(df)
    clean_cols = process_cols_v2(cols)
    df.columns = clean_cols
    cols_dict = gen_cols_dict(cols, clean_cols)
    df = process_csv_step_one(df)
    df = process_csv_step_two(df)
    ncols, cols_added = cols_for_export(list(df), cols_dict)
    df.columns = ncols
    #df = df[[i for i in ncols if i not in cols_added]]
    file = '/' + master_sku_file
    filename = '/'.join(filename.split('/')[:-1]) + file
    df.to_csv(filename, index=False)


if __name__ == '__main__':
    main()
