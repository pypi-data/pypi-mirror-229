# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['semantix_genai_inference',
 'semantix_genai_inference.inference',
 'semantix_genai_inference.inference.llm']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.8.4,<4.0.0', 'click>=8.1.4,<9.0.0']

entry_points = \
{'console_scripts': ['semantix-ai = semantix_genai_inference.cli:cli']}

setup_kwargs = {
    'name': 'semantix-genai-inference',
    'version': '0.0.3',
    'description': '',
    'long_description': "# Semantix GenAI Inference\n\nA python client library to help you interact with the Semantix GenAI Inference API.\n\n\n# Installation\n\nIf you're using pip, just install it from the latest release:\n\n    $ pip install semantix-genai-inference\n\nElse if you want to run local, clone this repository and install it with poetry:\n\n    $ poetry build\n    $ poetry install\n\n# Usage\n\nTo use it:\n\nFirst, make sure you have a valid API key. You can get one at [Semantix Gen AI Hub](https://home.ml.semantixhub.com/)\n\nSet an environment variable with your api secret:\n\n    $ export SEMANTIX_API_SECRET=<YOUR_API_SECRET>\n    $ semantix-ai --help\n\n# DEV - Publish to pypi\n\n    $ poetry config pypi-token.pypi <YOUR_PYPI_TOKEN>\n    $ poetry build\n    $ poetry publish\n\n# DEV - Bump version\n\n    $ poetry version patch | minor | major | premajor | preminor | prepatch | prerelease\n\nSee more at [Poetry version command docs](https://python-poetry.org/docs/cli/#version)\n\n# DEV - Commit message semantics\n\nSee at [Conventional Commits](https://gist.github.com/joshbuchea/6f47e86d2510bce28f8e7f42ae84c716)",
    'author': 'Dev Team',
    'author_email': 'dev@semantix.ai',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7',
}


setup(**setup_kwargs)
