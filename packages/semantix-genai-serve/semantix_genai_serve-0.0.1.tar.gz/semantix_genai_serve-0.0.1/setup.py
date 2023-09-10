# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['semantix_genai_serve', 'semantix_genai_serve.huggingface']

package_data = \
{'': ['*']}

install_requires = \
['accelerate==0.22.0', 'kserve==0.11.0', 'transformers>=4.28.0']

setup_kwargs = {
    'name': 'semantix-genai-serve',
    'version': '0.0.1',
    'description': '',
    'long_description': '',
    'author': 'Dev Team',
    'author_email': 'dev@semantix.ai',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.12',
}


setup(**setup_kwargs)
