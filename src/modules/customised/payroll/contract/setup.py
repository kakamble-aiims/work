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
name = 'trytond_contract'

download_url = 'http://downloads.tryton.org/%s.%s/' % (
    major_version, minor_version)
if minor_version % 2:
    version = '%s.%s.dev0' % (major_version, minor_version)
    download_url = (
        'hg+http://hg.tryton.org/modules/%s#egg=%s-%s' % (
            name[8:], name, version))

requires = ['python-sql >= 0.9']
for dep in info.get('depends', []):
    if not re.match(r'(ir|res)(\W|$)', dep):
        requires.append(get_require_version('trytond_%s' % dep))
requires.append(get_require_version('trytond'))

contracts_require = [get_require_version('proteus')]
dependency_links = []
if minor_version % 2:
    dependency_links.append('https://trydevpi.tryton.org/')

setup(name=name,
    version=version,
    description='Tryton module to contract of employees ',
    author='AIIMS CF',
    author_email='aiimscf@aiims.edu',
    url='http://www.aiims.edu/',
    download_url=download_url,
    package_dir={'trytond.modules.contract': '.'},
    packages=[
        'trytond.modules.contract',
        #'trytond.modules.contract.contracts',
        ],
    package_data={
        'trytond.modules.contract': (info.get('xml', [])
            + ['tryton.cfg', 'view/*.xml', 'locale/*.po', 'icons/*.svg',
            'contracts/*.rst']),
        },
    platforms='any',
    license='GPL-3',
    python_requires='>=3.4',
    install_requires=requires,
    dependency_links=dependency_links,
    zip_safe=False,
    entry_points="""
    [trytond.modules]
    contract = trytond.modules.contract 
    """,
    #contract_suite='contracts',
    #contract_loader='trytond.contract_loader:Loader',
    #contracts_require=contracts_require,
    )
'''
setup.py
Displaying setup.py.
'''
