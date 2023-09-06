# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['datahub_api', 'datahub_api.datahub']

package_data = \
{'': ['*'], 'datahub_api': ['config/*']}

install_requires = \
['Jinja2>=3.1.2,<4.0.0',
 'numpy>=1.22.0,<2.0.0',
 'retrying>=1.3.4,<2.0.0',
 'sqlglot>=18.1.0,<19.0.0',
 'toml>=0.10.2,<0.11.0']

setup_kwargs = {
    'name': 'datahub-api',
    'version': '0.1.0',
    'description': '',
    'long_description': '',
    'author': 'Haibo SUN',
    'author_email': 'haibo.sun@liveramp.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
