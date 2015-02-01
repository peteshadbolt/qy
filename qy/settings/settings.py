import os
import json
from qy.util import json_no_unicode

# the default settings, used when creating a settings file for the first time
defaults = {
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

# the default settings, used when creating a settings file for the first time
defaults = {
    'fpga.com': 5,
    'toptica.com': 6,
    'fpga.labels': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'AB', 'AD', 'BC', 'CD', 'EF', 'GH', 'DE', 'CF', 'FG', 'EH', 'ABCD', 'CDEF', 'EFGH', 'ABCDEFGH'],
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


def save(main_dict):
    f = open(qy_filename, 'w')
    json.dump(main_dict, f, indent=4, sort_keys=True)
    f.close()


def initialize():
    save(defaults)


def load():
    ''' Load the settings file into a dict '''
    if not os.path.exists(qy_filename):
        initialize()
    return json.load(open(qy_filename), object_hook=json_no_unicode)


def get(search):
    ''' Look up a search term and return its value'''
    main_dict = load()
    search = search.lower().strip()
    if search in main_dict:
        return main_dict[search]
    print '%s not found in qy settings file [%s]!' % (search, qy_filename)
    return None


def put(search, value):
    ''' Write a value to the database '''
    main_dict = load()
    search = search.lower().strip()
    main_dict[search] = value
    save(main_dict)

# Lookup the filename automatically
qy_filename = os.path.join(get_config_path(), 'qy.json')
main_dict = None

if __name__ == '__main__':
    print get_config_path()
    initialize()
    load()
    print get('realtime.scan.close_shutter')
    put('motors.com', 5)
    print get('motors.com')
