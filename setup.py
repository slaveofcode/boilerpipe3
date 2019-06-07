import tarfile
from fnmatch import fnmatch
from os.path import basename, exists, dirname, abspath, join
import setuptools

try:
    from urllib import urlretrieve
except:
    from urllib.request import urlretrieve

import sys

if sys.version_info[0] < 3:
    print("This module can only be used with Python 3.")
    print("For a Python 2 version, see:\nhttps://github.com/misja/python-boilerpipe")
    sys.exit(1)

__version__ = '1.2'
boilerpipe_version = '1.2.1'
DATAPATH = join(abspath(dirname((__file__))), 'boilerpipe/data')


def download_jars(datapath, version=boilerpipe_version):
    tgz_url = 'https://github.com/derlin/boilerpipe3/raw/master/boilerpipe-{0}-bin.tar.gz'.format(version)
    tgz_name = basename(tgz_url)

    if not exists(tgz_name):
        downloaded = urlretrieve(tgz_url, tgz_name)
        tgz_name = downloaded[0]

    tar = tarfile.open(tgz_name, mode='r:gz')
    for tarinfo in tar.getmembers():
        if not fnmatch(tarinfo.name, '*.jar'):
            continue
        tar.extract(tarinfo, datapath)


download_jars(datapath=DATAPATH)

setuptools.setup(
    name='boilerpipe3',
    version=__version__,
    author='Lucy Linder',
    author_email='lucy.derlin@gmail.com',
    url='https://github.com/derlin/boilerpipe3',

    packages=['boilerpipe'],
    package_data={
        'boilerpipe': [
            'data/boilerpipe-{version}/boilerpipe-{version}.jar'.format(version=boilerpipe_version),
            'data/boilerpipe-{version}/lib/*.jar'.format(version=boilerpipe_version),
        ],
    },
    install_requires=[
        'JPype1-py3',
        'requests',
        'beautifulsoup4',
    ],

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.4',
        'Natural Language :: English',
    ],

    keywords='boilerpipe',
    license='Apache 2.0',

    description='Python interface to Boilerpipe, Boilerplate Removal and Fulltext Extraction from HTML pages with Python 3 support. '
                'Forked and improved from https://github.com/slaveofcode/boilerpipe3.'
)
