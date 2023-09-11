# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['koi']

package_data = \
{'': ['*']}

modules = \
['__init__']
setup_kwargs = {
    'name': 'koi-x',
    'version': '0.0.1',
    'description': 'koi - Pytorch',
    'long_description': '[![Multi-Modality](agorabanner.png)](https://discord.gg/qUtxnK2NMf)\n\n# Koi\nA simple pytorch implementation of a meta learning algorithm from OPENAI "Reptile: A scalable meta-learning algorithm"\n\n\n\n# Appreciation\n* Lucidrains\n* Agorians\n\n\n\n# Install\n\n# Usage\n\n\n# License\nMIT\n\n',
    'author': 'Kye Gomez',
    'author_email': 'kye@apac.ai',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/kyegomez/koi',
    'packages': packages,
    'package_data': package_data,
    'py_modules': modules,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
