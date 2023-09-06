# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['notebridge']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=2.2.1,<3.0.0', 'requests>=2.31.0,<3.0.0']

setup_kwargs = {
    'name': 'notebridge',
    'version': '0.2.0',
    'description': 'Notebridge is a tool to connect NoteAid app to your user-defined agent.',
    'long_description': '<img src="https://imagedelivery.net/Dr98IMl5gQ9tPkFM5JRcng/19234312-c06c-4c78-76de-f4618543b400/Ultra" alt="BloArk" />\n\n# Notebridge\n\nNotebridge is an adapter library in Python, lying between your NoteAid agent and the actual NoteAid API. It provides a simple interface to define your agent and to connect it to the NoteAid chat API.\n\n## Installation\n\nThe package is available on PyPI and can be installed using pip:\n\n```bash\npip install notebridge\n```\n',
    'author': 'Lingxi Li',
    'author_email': 'hi@lingxi.li',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://notebridge.lingxi.li/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4',
}


setup(**setup_kwargs)
