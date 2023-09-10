# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['scpca']

package_data = \
{'': ['*']}

install_requires = \
['adjusttext>=0.7.3,<0.8.0',
 'gseapy>=1.0.4,<2.0.0',
 'pyro-ppl<1.8.4',
 'scanpy>=1.8.2',
 'torch<2.0.0']

extras_require = \
{'docs': ['Sphinx==7.0.1',
          'sphinx-rtd-theme==1.3.0',
          'sphinxcontrib-napoleon==0.7',
          'nbsphinx==0.8.9',
          'sphinx-autodoc-typehints==1.24.0'],
 'notebook': ['jupyter']}

setup_kwargs = {
    'name': 'scpca',
    'version': '0.1.0',
    'description': 'Single-cell PCA.',
    'long_description': '# scPCA\n\nThis is the upcomint scCPA package.\n',
    'author': 'Harald Vohringer',
    'author_email': 'harald.voeh@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8.1,<3.11',
}


setup(**setup_kwargs)
