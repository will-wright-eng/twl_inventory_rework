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

from modules.utility_fxns import list_files_in_directory,process_cols_v2,gen_cols_dict,distribute,cols_for_export
from modules.ls_fxns_base import sku_combo_dicts_v2,gen_prod_matrix,extract_and_dict

def main():
	today = str(dt.datetime.today()).split(' ')[0]
	file_list = list_files_in_directory('.')
	filename0 = [i for i in file_list if master_sku_file in i][0]
	filename1 = [i for i in file_list if ls_product_export in i][0]
	print(filename1)
	df,id_dict,cols_dict = extract_and_dict(file_list,master_sku_file,filename1,filename0)
	mfg_code = 'DIS'
	msets = []
	color_dicts,weight_dict = sku_combo_dicts_v2(file_list)
	for prod in list(id_dict):
	    return_flag,matrix = gen_prod_matrix(df,id_dict,mfg_code,prod,color_dicts,weight_dict)
	    if return_flag:
	        msets.append(matrix)
	df = pd.concat(msets,axis=0)
	df = df.dropna(axis=1, how='all')
	df = df.fillna('')
	ncols, cols_added = cols_for_export(list(df),cols_dict)
	df.columns = ncols
	#df = df[[i for i in ncols if i not in cols_added]]
	file = '/data_imports/'+today+'_ls_import_table.csv'
	filename = '/'.join(filename1.split('/')[:-3])+file
	df.to_csv(filename,index=False)

if __name__ == '__main__':
    main()
