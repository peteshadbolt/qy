#!/usr/bin/python
import subprocess
from glob import glob
import os
import difflib


def process(filename):
    """ Apply autopep8 and list diff """
    pepper = subprocess.Popen(["autopep8", filename], stdout=subprocess.PIPE)
    pepped = [line for line in pepper.stdout]

    print filename
    f = open(filename, "w")
    f.write("".join(pepped))
    f.close()


if __name__ == '__main__':
    root = "/home/pete/physics/libraries/qy_new/"
    os.chdir(root)
    for path, dirs, files in os.walk(root):
        files = filter(lambda x: x.endswith(".py"), files)
        for f in files:
            process(os.path.join(path, f))
