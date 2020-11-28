'''
Author: William Wright
'''

import re

class clean_description(object):
    '''clean_description docstring'''
    def __init__(self, desc):
        self.desc = desc
        
    def clean(self):
        self.d = self.flight_chars_dict()
        self.desc = self.remove_content()
        self.desc = self.substitution()
        if len(self.d)>0:
            self.desc = self.add_flight_chars(self.d)
        return self.desc

    def flight_chars_dict(self):
        patterns = ['title="speed-(.+?)gif','title="glide-(.+?)gif','title="turn-(.+?)gif','title="fade-(.+?)gif']
        cats = ['speed','glide','turn','fade']
        d = {}
        for pattern, cat in zip(patterns,cats):
            match = re.findall(pattern,self.desc)
            if len(match)==1:
                d[cat] = match[0].replace('.','')
        return d

    def remove_content(self):
        ''' docstring for remove_content
        - remove "Info about plastic" section
        - remove everything after "more information"
        - remove everything before the first paragraph tag'''
        regex_dict = {
            '<h3>FLIGHT CHARACTERISTICS</h3>.+?</a></p>':'',
            # ' <p><span style.+?>Please note.+?</span></p>':'',
            '<p>Information about <a title="Information about this plastic type.+?</p>':'',
            '</ul> <h3>More Information</h3> <p>.+':'',
            '<h3>SPECIFICATIONS</h3>.+?<li>Best':'<h3>SPECIFICATIONS</h3> <ul> <li>Best',
            'Check out how it flies here.</p> <p><!-- mceItemMediaService.+?mceItemMediaService --></p>':''
            }
        for pattern in regex_dict:
            self.desc = re.sub(pattern,regex_dict[pattern],self.desc)

        i = self.desc.find('<p>')
        if i==-1:
            pass
        else:
            self.desc = self.desc[i:]

        return self.desc
    
    def substitution(self):
        '''substitution docstring'''
        def sub_pattern(pattern,sub1,sub2,funk):
            pattern_list = re.findall(pattern,self.desc)
            if len(pattern_list)>0:
                for i,j in zip(pattern_list,[funk(i) for i in pattern_list]):
                    self.desc = re.sub(sub1.format(i),sub2.format(j),self.desc)

        pattern = '<h3>(.+?)</h3>'
        sub1 = '<h3>{}</h3>'
        sub2 = '<h2>{}</h2>'
        funk = str.title
        sub_pattern(pattern,sub1,sub2,funk)

        pattern = '<li>(.+?)</li>'
        sub1 = '<li>{}</li>'
        funk = str.capitalize
        sub_pattern(pattern,sub1,sub1,funk)

        pattern = '<p><span style.+?;">([A-Z].+?)</span></p>'
        sub1 = '<p><span style.+?;">{}</span></p>'
        sub2 = '<p>{}</p>'
        funk = str
        sub_pattern(pattern,sub1,sub1,funk)

        return self.desc

    def add_flight_chars(self,d):
        '''add_chars docstring
        appends bullet list of flight chars to end'''
        s1 = ' / '.join([d[i] for i in d])
        s2 = ' / '.join([i for i in d])
        s3 = '<li>Flight characteristics: {} ({})</li>'.format(s1,s2)
        s3 = s3.replace('zero','0')
        s3 = s3.replace('minus','')
        note = '<li>Please note: stamp & exact color may vary</li></ul>'
        return self.desc+s3+note