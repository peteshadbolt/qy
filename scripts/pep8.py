import subprocess
from glob import glob
import os
import difflib

def process(filename):
    """ Apply autopep8 and list diff """
    original = open(filename).readlines()
    pepper = subprocess.Popen(["autopep8", filename], stdout=subprocess.PIPE)
    pepped = [line for line in pepper.stdout]

    d = difflib.Differ()
    for diff in d.compare(original, pepped):
        print diff.strip()
    

    raw_input()


if __name__ == '__main__':
    root = os.path.join(os.path.dirname(__file__), "../")
    os.chdir(root)
    for path, dirs, files in os.walk(root):
        files = filter(lambda x: x.endswith(".py"), files)
        for f in files:
            process(os.path.join(path, f))


