import os
import json

# the default settings, used when creating a settings file for the first time
defaults={  \
'motors.com': 3,
'motors.count': 2,
'dpc320.photon_buffer_1': 'F:\photon_buffer_1',
'dpc320.photon_buffer_2': 'F:\photon_buffer_2',
'data.directory': 'C:\Documents and Settings\phpjss\Desktop\test_data',
'data.temp': 'F:\temporary_data',
'chameleon.com': 7,
'realtime.coincidence_window': 30,
'realtime.sound': 1,
'realtime.browser_searches': ('A', 'B', 'C'),
'realtime.scan.start_position': 0.0,
'realtime.scan.stop_position': 5.0,
'realtime.scan.npoints': 5,
'realtime.scan.nloops': 3,
'realtime.scan.integration_time': 2,
'realtime.scan.motor_controller': 2,
'realtime.scan.dont_move': 0,
'realtime.scan.close_shutter': 0,
'realtime.watcher.singles_patterns': ('A',),
'realtime.watcher.coincidence_patterns': ('AB',)
}

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

def initialize():
    main_dict=defaults.copy()
    f=open(qy_filename, 'w')
    f.write(json.dumps(main_dict))
    f.close()
    print 'Generated a new settings file for qy [%s]' % qy_filename

def load():
    ''' Load the settings file into a dict '''
    if os.path.exists(qy_filename):
        return json.loads(open(qy_filename).read())
    else:
        initialize()

def get(search):
    ''' Look up a search term and return its value'''
    main_dict=load()
    search=search.lower().strip()
    if search in main_dict: return main_dict[search]
    print '%s not found in qy settings file [%s]!' % (search, qy_filename)
    return None
            
def put(search, value):
    ''' Write a value to the database '''
    main_dict=load()
    search=search.lower().strip()
    main_dict[search]=value
    f=open(qy_filename, 'w')
    f.write(json.dumps(main_dict))
    f.close()
    
# Lookup the filename automatically 
qy_filename=os.path.join(get_config_path(), 'qy.json')

if __name__=='__main__':
    initialize()
    load()
    print get('realtime.scan.close_shutter')

