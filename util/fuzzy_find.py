import os

class fuzzy_finder:
    def __init__(self, root, suffix='', extra_filter=None):
        ''' helpful for finding files without putting massive great paths in scripts '''
        self.root=root
        self.all_files=[]
        for root,dirs,files in os.walk(root):
            self.all_files+=map(lambda x: os.path.join(root, x), files)
        self.all_files=filter(lambda x: x.endswith(suffix), self.all_files)
        if extra_filter!=None:
            self.all_files=filter(lambda x: extra_filter in x, self.all_files)

    def get_all_files(self):
        ''' get the list of all files '''
        return list(self.all_files)

    def find(self, substring):
        ''' fuzzy-find a file and return its path '''
        for item in self.all_files:
            if substring in item: return item
        print '%s not found!!!' % substring
        raw_input()

    def find_many(self, substrings):
        ''' fuzzy-find a list of files and return its path '''
        items=[]
        for item in self.all_files:
            if all([(substring in item) for substring in substrings]): items.append(item)
        if len(items)>=1: return items
        print '%s not found!!!' % substring
        raw_input()

    def __str__(self):
        ''' convert to string '''
        return '\n'.join(self.all_files)
