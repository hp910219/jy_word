# -*- coding: utf-8 -*-
# !/usr/bin/python
# Create Date 2018/8/23 0023
__author__ = 'huohuo'
import os
from git import Repo


def clc_dist():
    delDir = "dist"
    for f in os.listdir(delDir):
        filePath = os.path.join(delDir, f)
        os.remove(filePath)
        print filePath + " was removed!"


def update_version(version):
    s = '''# -*- coding: utf-8 -*-
# !/usr/bin/python
# Create Date 2018/6/4 0004
__author__ = 'huohuo'
from setuptools import setup, find_packages

setup(
    name='jy-word',
    version='%.2f',
    keywords=('word', 'test'),
    description='generate word',
    license='MIT License',
    author='hp910219',
    author_email='hp910219@126.com',
    url='https://github.com/hp910219/jy-word.git',
    packages=find_packages(exclude=['test']),
    # 需要安装的依赖
    install_requires=['pillow'],
    # data_files=[('demo', ['demo.xml'])]
)

if __name__ == "__main__":
    pass''' % version
    f = open('setup.py', 'w')
    f.write(s)


def upload_code():
    repo = Repo('.git')
    remote = repo.remote()
    remote.pull()
    repo.commit('master')
    remote.push()


# upload_code()
update_version(1.34)
clc_dist()
os.system('python setup.py sdist check')
os.system('python setup.py sdist')
# twine upload dist/*
# pip install jy-word --upgrade
# os.system("cmd/c start twine upload dist/*")
# os.system("pip install jy-word --upgrade")
# commands.getstatusoutput('python setup.py sdist upload')
# status, output = commands.getstatusoutput('twine upload dist/*')


if __name__ == "__main__":
    pass
    

