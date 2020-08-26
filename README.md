# The Wright Life -- Inventory Rework

This repo contains code used in processing inventory tables from BigCommerce (BC) and Lightspeed (LS).

## General workflow thus far

1. downloaded inventory from BC
2. munged for Discraft product list (bc_fxns_preprocess & filter_down_bc_product_list)
3. developed bc_fxns_base and bc_fxns_core to generate BC import table
	- single product test successful
4. reworked bc_fxns into ls_fxns_base to generate LS import table (no tests yet)
5. repo cleanup

### _File Dependencies_
![file_dependencies](https://github.com/william-cass-wright/twl_inventory_rework/blob/master/images/file_dependencies.png)

### _Directory_
![directory](https://github.com/william-cass-wright/twl_inventory_rework/blob/master/images/directory.png)

## TO DO
### _Need_

- ~~add sku modifier so that skus sort properly (parent then all child rows; add modifier, sort, remove modifier)~~
- update linked skus in LS, then BC once LS is confirmed (test skus then in-bulk)
- start planning Amazon/Cadisto implementation

### _Want_

- file names and product lists are hard coded --> parameterize!
- ~~replace jupyter notebooks with shell scripts~~
- API calls to BC and LS systems for inventory download/upload (if possible, check docs)

### _Nice to have_

- bc_fxns_preprocess & filter_down_bc_product_list need to be combined and generalized to all products
	- only utilized in downstream code for sku list and product cateogry

## Important notes

- parent/child orientation in BC import table is essential to successful update

## References

_Anatomy of each system_

- import spreadsheet template
- product hierarchy (Product: SKU, Item: Matrix, etc)
- inventory attributes (price, quantity, vendor, description, etc)

__LightSpeed__

- Importing inventory data: https://retail-support.lightspeedhq.com/hc/en-us/articles/229129988-Importing-inventory-data
- Formatting item import files: https://retail-support.lightspeedhq.com/hc/en-us/articles/115005142408-Formatting-item-import-files
- Creating matrices: https://retail-support.lightspeedhq.com/hc/en-us/articles/229130188-Creating-matrices
- Formatting matrix for import: https://retail-support.lightspeedhq.com/hc/en-us/articles/115005187687

__BigCommerce__

- Importing and Exporting Products: https://support.bigcommerce.com/s/article/Importing-Exporting-Products#product-import
- Troubleshooting | Data Import/Export: https://support.bigcommerce.com/s/article/Troubleshooting-Data-Import-Export#excel
- Importing Product Options (v3): https://support.bigcommerce.com/s/article/Importing-Product-Options-v3

__Amazon__

- Manage your inventory in bulk: https://sellercentral.amazon.com/gp/help/help-page.html?itemID=9DZLGS87GVDT94B&ref=au_9DZLGS87GVDT94B_bred_201201070