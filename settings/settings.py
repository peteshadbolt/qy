import os
import json

def get_config_path():
    ''' Platform-independent way to choose a location for qy settings '''
    if 'APPDATA' in os.environ:
        confighome = os.environ['APPDATA']
    elif 'XDG_CONFIG_HOME' in os.environ:
        confighome = os.environ['XDG_CONFIG_HOME']
    else:
        confighome = os.path.join(os.environ['HOME'], '.config')
    configpath = os.path.join(confighome, 'qy')
    return configpath

def initialize(prototype={}):
    ''' Should only be called when you first install qy. This makes a blank JSON file '''
    if not raw_input('You are about to overwrite all qy settings. Continue? ').startswith('y'):
        print 'Cancelled.'
        return
    f=open(qy_filename, 'w')
    f.write(json.dumps(prototype), sort_keys=True, indent=4)
    f.close()
    print 'Created a qy JSON settings file at %s' % qy_filename

def load():
    ''' Load the settings file into a dict '''
    f=open(qy_filename)
    s=f.read()
    f.close()
    return json.loads(s)

def get(search):
    ''' Look up a search term and return its value'''
    main_dict=load()
    search=search.lower().strip()
    if search in main_dict: return main_dict[search]
    print '%s not found in settings file (%s)!' % (search, qy_filename)
    return None
            
def put(search, value):
    ''' Write a value to the database '''
    main_dict=load()
    search=search.lower().strip()
    main_dict[search]=value
    f=open(qy_filename, 'w')
    f.write(json.dumps(main_dict), indent=4, sort_keys=True)
    f.close()

# Lookup the filename automatically 
qy_filename=os.path.join(get_config_path(), 'qy.json')

if __name__=='__main__':
    print load()

