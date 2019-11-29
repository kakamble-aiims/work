#!/usr/bin/env python3
# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

import io
import os
import re
from configparser import ConfigParser
from setuptools import setup


def read(fname):
    return io.open(
        os.path.join(os.path.dirname(__file__), fname),
        'r', encoding='utf-8').read()


def get_require_version(name):
    if minor_version % 2:
        require = '%s >= %s.%s.dev0, < %s.%s'
    else:
        require = '%s >= %s.%s, < %s.%s'
    require %= (name, major_version, minor_version,
                major_version, minor_version + 1)
    return require


config = ConfigParser()
config.read_file(open('tryton.cfg'))
info = dict(config.items('tryton'))
for key in ('depends', 'extras_depend', 'xml'):
    if key in info:
        info[key] = info[key].strip().splitlines()
version = info.get('version', '0.0.1')
major_version, minor_version, _ = version.split('.', 2)
major_version = int(major_version)
minor_version = int(minor_version)

health_version = '3.4'

name = 'trytond_aiims_health_extn'

download_url = 'http://downloads.tryton.org/%s.%s/' % (
    major_version, minor_version)
if minor_version % 2:
    version = '%s.%s.dev0' % (major_version, minor_version)
    download_url = (
        'hg+http://hg.tryton.org/modules/%s#egg=%s-%s' % (
            name[8:], name, version))

requires = ['python-sql >= 0.9']
for dep in info.get('depends', []):
    if (dep == 'health'):
        requires.append('gnuhealth == %s' % (health_version))

    elif dep.startswith('health_'):
        health_package = dep.split('_',1)[1]
        requires.append('gnuhealth_%s == %s' %
            (health_package, health_version))
    else: 
        if not re.match(r'(ir|res|webdav)(\W|$)', dep):
            requires.append('trytond_%s >= %s.%s, < %s.%s' %
                (dep, major_version, minor_version, major_version,
                    minor_version + 1))

requires.append(get_require_version('trytond'))

tests_require = [get_require_version('proteus')]
dependency_links = []
if minor_version % 2:
    dependency_links.append('https://trydevpi.tryton.org/')

setup(
    name=name,
    version=version,
    description='Manage various masters for aiimsS',
    author='aiimsS CF',
    author_email='aiimsscf@aiimss.edu',
    url='http://www.aiimss.edu/',
    download_url=download_url,
    package_dir={'trytond.modules.aiims_health_extn': '.'},
    packages=[
        'trytond.modules.aiims_health_extn',
        #'trytond.modules.aiims_health_extn.tests',
        ],
    package_data={
        'trytond.modules.aiims_health_extn': (info.get('xml', [])
            + ['tryton.cfg', 'view/*.xml', 'locale/*.po', 'icons/*.svg',
            'tests/*.rst', 'data/*.xml']),
        },
    platforms='any',
    license='GPL-3',
    python_requires='>=3.4',
    install_requires=requires,
    dependency_links=dependency_links,
    zip_safe=False,
    entry_points="""
    [trytond.modules]
    aiims_health_extn = trytond.modules.aiims_health_extn
    """,
    #test_suite='tests',
    #test_loader='trytond.test_loader:Loader',
    #tests_require=tests_require,
    )
