import os
import pandas as pd
import string
import re

def list_files_in_directory(path):
    '''docstring for list_files_in_directory'''
    x = []
    cwd = os.getcwd()
    for root, dirs, files in os.walk('.'+path):
        for file in files:
            #print(root+'/'+file)
            x.append(root+'/'+file)
    return x

def process_cols(cols,purpose='for processing'):
	'''docstring for process_cols
	for processing: remove special characters
	'''
	clean = [i.lower().replace(' ','_').replace('+','').replace('/','_').replace('?','').replace('-','').replace('__','_').replace('t.','t') for i in cols]
	return clean

def process_cols_v2(cols,purpose='for processing'):
	'''docstring for process_cols
	for processing: remove special characters
	'''
	chars = re.escape(string.punctuation)
	clean = [re.sub(r'['+chars+']', '',my_str) for my_str in cols]
	clean = [i.lower().replace(' ','_') for i in clean]
	return clean

def gen_cols_dict(cols,clean_cols):
	'''docstring for gen_cols_dict'''
	cols_dict = {i:j for (i,j) in zip(clean_cols,cols)}
	return cols_dict

def distribute(oranges, plates):
	'''docstring for distribute'''
	base, extra = divmod(oranges, plates)
	return [base + (i < extra) for i in range(plates)]

def df_stats(df):
	'''docstring for df_stats'''
	dfs = [pd.DataFrame(df.count())
		, pd.DataFrame(100*df.count()/len(df))
		, pd.DataFrame(df.dtypes)]
	d = pd.concat(dfs,axis=1)
	d.columns = ['value_counts','percent','type']
	d = d.merge(set_len_col(df),left_index=True,right_index=True,how='left')
	cols = list(d.loc[d['percent']>99].index)
	d = d.sort_values(by='value_counts', ascending=False)
	return d, cols

class df_processing(object):
	'''docstring for df_processing class'''
	def __init__(self,filename,auto_run=True):
		self.filename = filename
		if auto_run:
			df = self.run_process(self.filename)
			self.df = df
			cols = list(df)
			self.cols = cols
	def run_process(self,filename):
		df = pd.read_csv(filename)
		self.raw_df = df
		df.columns = self.process_cols(self.cols)
		return df
	def process_cols(self,cols,purpose='for processing'):
		if purpose=='for processing':
			clean = [i.lower().replace(' ','_').replace('+','').replace('/','_').replace('?','').replace('-','').replace('__','_').replace('.','') for i in self.cols]
			cols_dict = {i:j for (i,j) in zip(clean,self.cols)}
			self.cols_dict = cols_dict
		elif purpose=='for import':
			clean = [self.cols_dict[i] for i in cols]
		else:
			raise ValueError('valid inputs for process_cols are either "for processing" or "for import"')
		return clean