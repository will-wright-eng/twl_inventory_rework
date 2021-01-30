#!/bin/bash

bc_product_export="products-2020-08-25.csv"
ls_product_export="2020-08-17_item_listings_local_matches.csv"
master_sku_file="master_list_discraft_skus.csv"

export bc_product_export
export ls_product_export
export master_sku_file

python3 ./bc_product_master_list.py 
python3 ./bc_import_table.py
python3 ./ls_import_table.py