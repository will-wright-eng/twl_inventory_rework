# Inventory Rework
## Contents

- Summary

## Summary

Converting product variance found in BigCommerce 'Bulk Edit' catalog export to Lightspeed bulk product import template -- thereby standardizing product variance accross product categories

### _Modules_
![file_dependencies](https://github.com/william-cass-wright/twl_inventory_rework/blob/master/images/file_dependencies.png)

### _Inventory Rework Directory_
![directory](https://github.com/william-cass-wright/twl_inventory_rework/blob/master/images/directory.png)

## TO DO
### _Need_

- ~~add sku modifier so that skus sort properly (parent then all child rows; add modifier, sort, remove modifier)~~
- ~~update linked skus in LS, then BC once LS is confirmed (test skus then in-bulk)~~
- ~~start planning Amazon/Cadisto implementation~~
- NEXT: parameterize vendor and refactor categories to standard disc golf models

### _Want_

- file names and product lists are hard coded --> parameterize!
- ~~replace jupyter notebooks with shell scripts~~
- API calls to BC and LS systems for inventory download/upload (if possible, check docs)
- organize directory such that repo can be cloned into place then run

### _Nice to have_

- bc_fxns_preprocess & filter_down_bc_product_list need to be combined and generalized to all products
	- only utilized in downstream code for sku list and product cateogry
- complete [package tutorial](https://packaging.python.org/tutorials/packaging-projects/) 
	- setup.py
	- standardized naming like lib and utils 
- refactor base and core fxns into classes

## Important notes

- parent/child orientation in BC import table is essential to successful update
- BC option sets can duplicate as a product of importing... still not sure why -- insure unique option set naming

## References

_Anatomy of each system_

- inventory import template
- product hierarchy (Product: SKU, Item: Matrix, Parent: Child, etc)
- inventory attributes (price, quantity, vendor, description, etc)

__LightSpeed__

- [Importing inventory data](https://retail-support.lightspeedhq.com/hc/en-us/articles/229129988-Importing-inventory-data)
- [Formatting item import files](https://retail-support.lightspeedhq.com/hc/en-us/articles/115005142408-Formatting-item-import-files)
- [Creating matrices](https://retail-support.lightspeedhq.com/hc/en-us/articles/229130188-Creating-matrices)
- [Formatting matrix for import](https://retail-support.lightspeedhq.com/hc/en-us/articles/115005187687)

__BigCommerce__

- [Importing and Exporting Products](https://support.bigcommerce.com/s/article/Importing-Exporting-Products#product-import)
- [Troubleshooting | Data Import/Export](https://support.bigcommerce.com/s/article/Troubleshooting-Data-Import-Export#excel)
- [Importing Product Options (v3)](https://support.bigcommerce.com/s/article/Importing-Product-Options-v3)

__Amazon__

- [Manage your inventory in bulk](https://sellercentral.amazon.com/gp/help/help-page.html?itemID=9DZLGS87GVDT94B&ref=au_9DZLGS87GVDT94B_bred_201201070)
