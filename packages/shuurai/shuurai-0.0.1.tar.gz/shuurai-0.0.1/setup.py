# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['shuurai']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'shuurai',
    'version': '0.0.1',
    'description': 'shuurai - Pytorch',
    'long_description': '[![Multi-Modality](agorabanner.png)](https://discord.gg/qUtxnK2NMf)\n\n# Paper-Implementation-Template\nA simple reproducible template to implement AI research papers \n\nPaper Link\n\n# Appreciation\n* Lucidrains\n* Agorians\n\n\n\n# Install\n\n# Usage\n\n# Architecture\n\n# Todo\n\n\n# License\nMIT\n\n# Citations\n\n',
    'author': 'Kye Gomez',
    'author_email': 'kye@apac.ai',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/kyegomez/shuurai',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
