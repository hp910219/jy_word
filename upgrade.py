# -*- coding: utf-8 -*-
# !/usr/bin/python
# Create Date 2018/8/23 0023
__author__ = 'huohuo'
import os


def clc_dist():
    delDir = "dist"
    for f in os.listdir(delDir):
        filePath = os.path.join(delDir, f)
        os.remove(filePath)
        print filePath + " was removed!"

clc_dist()
os.system('python setup.py sdist check')
os.system('python setup.py sdist')
# os.system("cmd/c start twine upload dist/*")
# os.system("pip install jy-word --upgrade")
# commands.getstatusoutput('python setup.py sdist upload')
# status, output = commands.getstatusoutput('twine upload dist/*')


if __name__ == "__main__":
    pass
    

