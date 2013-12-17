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

def load():
    ''' Load the settings file into a dict '''
    return json.loads(open(qy_filename).read())

def lookup(search):
    ''' Look up a search term and return its value'''
    main_dict=load()
    search=search.lower().strip()
    if search in main_dict: return main_dict[search]
    print '%s not found in settings file (%s)!' % (search, qy_filename)
    return None
            
def write(search, value):
    ''' Write a value to the database '''
    main_dict=load()
    search=search.lower().strip()
    main_dict[search]=value
    f=open(qy_filename, 'w')
    f.write(json.dumps(main_dict))
    f.close()
    
def save():
    ''' Obsolete '''
    print 'qy.settings.save is obsolete'

# Lookup the filename automatically 
qy_filename=os.path.join(get_config_path(), 'qy.json')

if __name__=='__main__':
    print load()

