import os
import json
from util import json_no_unicode

def get_path():
    """ Get the path of the settings file """
    root = os.path.dirname(__file__)
    return os.path.join(root, "settings.json")

def save():
    """ Save the settings file """
    global main_dict
    f = open(get_path(), 'w')
    json.dump(main_dict, f, indent=4, sort_keys=True)
    f.close()

def load():
    global main_dict
    settings_file = open(get_path())
    main_dict = json.load(settings_file, object_hook=json_no_unicode)
    settings_file.close()

def get(search):
    ''' Look up a search term and return its value'''
    global main_dict
    search = search.lower().strip()
    if search in main_dict:
        return main_dict[search]
    print '%s not found in qy settings file [%s]!' % (search, get_path())
    return None

def put(search, value):
    ''' Write a value to the database '''
    global main_dict
    search = search.lower().strip()
    main_dict[search] = value
    save(main_dict)

main_dict = {}
load()
        
