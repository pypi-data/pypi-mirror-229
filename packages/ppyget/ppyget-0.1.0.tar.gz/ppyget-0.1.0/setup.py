# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['ppyget']
install_requires = \
['aiohttp[speedups]>=3.8.5,<4.0.0']

setup_kwargs = {
    'name': 'ppyget',
    'version': '0.1.0',
    'description': 'pretty parallel yellow get - file downloader',
    'long_description': None,
    'author': 'technillogue',
    'author_email': 'technillogue@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
