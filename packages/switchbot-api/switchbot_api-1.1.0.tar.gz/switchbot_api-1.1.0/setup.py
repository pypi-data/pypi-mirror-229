# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['switchbot_api']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.8.4,<4.0.0']

setup_kwargs = {
    'name': 'switchbot-api',
    'version': '1.1.0',
    'description': 'An asynchronous library to use Switchbot API',
    'long_description': '# py-switchbot-api\nAn asynchronous library to use Switchbot API. Allows to use both devices and remotes.\n\n## Usage\n\n```python\ntoken = "xxx"\nsecret = "yyy"\n\nclient = SwitchBotAPI(token, secret)\nprint(await client.list_devices())\nprint(await client.get_status(\'some-id\'))\nawait client.send_command(\'some-id\', {COMMAND})\n```',
    'author': 'Ravaka Razafimanantsoa',
    'author_email': 'contact@ravaka.dev',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/SeraphicCorp/py-switchbot-api',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
