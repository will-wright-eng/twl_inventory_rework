'''
Author: William Wright
'''

class clean_description(object):
    '''clean_description docstring'''
    def __init__(self, desc):
        self.desc = desc
        
    def clean(self):
        self.d = self.flight_chars_dict()
        self.desc = self.remove_content()
        self.desc = self.clean_titles()
        if len(self.d)>1:
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
        # remove "Info about plastic" section
        # remove everything after more information'''
        regex_dict = {'<h3>FLIGHT CHARACTERISTICS</h3> <div>.+?</a></p>':'',
                      '<p>Information about <a title="Information about this plastic type.+?</p>':'',
                      '</ul> <h3>More Information</h3> <p>.+':'',
                     '<h3>SPECIFICATIONS</h3>.+?<li>Best':'<h3>SPECIFICATIONS</h3> <ul> <li>Best',
                     'Check out how it flies here.</p> <p><!-- mceItemMediaService.+?mceItemMediaService --></p>':''}
        for pattern in regex_dict:
            self.desc = re.sub(pattern,regex_dict[pattern],self.desc)
        return self.desc
    
    def clean_titles(self):
        # eself.desctract h3 titles
        # loop through un-modified titles and sub title-case titles with h2 in place of h3
        h3_titles = re.findall('<h3>(.+?)</h3>',self.desc)
        h3 = '<h3>{}</h3>'
        h2 = '<h2>{}</h2>'
        for i,j in zip(h3_titles,[i.title() for i in h3_titles]):
            self.desc = re.sub(h3.format(i),h2.format(j),self.desc)
        return self.desc

    def add_flight_chars(self,d):
        '''add_chars docstring
        appends bullet list of flight chars to end'''
        s1 = '/ '.join([d[i] for i in d])
        s2 = '/ '.join([i for i in d])
        s3 = '<li>Flight Characteristics: {} ({})</li>'.format(s1,s2)
        s3 = s3.replace('zero','0')
        s3 = s3.replace('minus','')
        note = '<li>Please note: stamp and exact color may vary</li></ul>'
        return self.desc+s3+note