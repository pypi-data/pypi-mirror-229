# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ape_roll']

package_data = \
{'': ['*']}

install_requires = \
['eth-ape>=0.6.18,<0.7.0']

setup_kwargs = {
    'name': 'ape-roll',
    'version': '0.0.1',
    'description': 'Build weiroll transactions with ape',
    'long_description': None,
    'author': 'FP',
    'author_email': 'fp@noemail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.12',
}


setup(**setup_kwargs)
