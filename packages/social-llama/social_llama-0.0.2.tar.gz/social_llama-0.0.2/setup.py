# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['social_llama', 'social_llama.data_processing', 'social_llama.training']

package_data = \
{'': ['*']}

install_requires = \
['accelerate>=0.22.0,<0.23.0',
 'bitsandbytes>=0.41.1,<0.42.0',
 'click>=8.0.1',
 'datasets>=2.14.4,<3.0.0',
 'peft>=0.5.0,<0.6.0',
 'scipy>=1.11.2,<2.0.0',
 'torch>=2.0.1,<3.0.0',
 'transformers>=4.32.1,<5.0.0',
 'trl>=0.7.1,<0.8.0']

entry_points = \
{'console_scripts': ['social-llama = social_llama.__main__:main']}

setup_kwargs = {
    'name': 'social-llama',
    'version': '0.0.2',
    'description': 'Social Llama',
    'long_description': "# Social Llama\n\n[![PyPI](https://img.shields.io/pypi/v/social-llama.svg)][pypi status]\n[![Status](https://img.shields.io/pypi/status/social-llama.svg)][pypi status]\n[![Python Version](https://img.shields.io/pypi/pyversions/social-llama)][pypi status]\n[![License](https://img.shields.io/pypi/l/social-llama)][license]\n\n[![Read the documentation at https://social-llama.readthedocs.io/](https://img.shields.io/readthedocs/social-llama/latest.svg?label=Read%20the%20Docs)][read the docs]\n[![Tests](https://github.com/AGMoller/social-llama/workflows/Tests/badge.svg)][tests]\n[![Codecov](https://codecov.io/gh/AGMoller/social-llama/branch/main/graph/badge.svg)][codecov]\n\n[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]\n[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]\n\n[pypi status]: https://pypi.org/project/social-llama/\n[read the docs]: https://social-llama.readthedocs.io/\n[tests]: https://github.com/AGMoller/social-llama/actions?workflow=Tests\n[codecov]: https://app.codecov.io/gh/AGMoller/social-llama\n[pre-commit]: https://github.com/pre-commit/pre-commit\n[black]: https://github.com/psf/black\n[license]: https://opensource.org/licenses/MIT\n\n## Features\n\n- TODO\n\n## Requirements\n\n- TODO\n\n## Installation\n\nYou can install _Social Llama_ via [pip] from [PyPI]:\n\n```console\n$ pip install social-llama\n```\n\n## Usage\n\nPlease see the [Command-line Reference] for details.\n\n## Contributing\n\nContributions are very welcome.\nTo learn more, see the [Contributor Guide].\n\n## License\n\nDistributed under the terms of the [MIT license][license],\n_Social Llama_ is free and open source software.\n\n## Issues\n\nIf you encounter any problems,\nplease [file an issue] along with a detailed description.\n\n## Credits\n\nThis project was generated from [@cjolowicz]'s [Hypermodern Python Cookiecutter] template.\n\n[@cjolowicz]: https://github.com/cjolowicz\n[pypi]: https://pypi.org/\n[hypermodern python cookiecutter]: https://github.com/cjolowicz/cookiecutter-hypermodern-python\n[file an issue]: https://github.com/AGMoller/social-llama/issues\n[pip]: https://pip.pypa.io/\n\n<!-- github-only -->\n\n[license]: https://github.com/AGMoller/social-llama/blob/main/LICENSE\n[contributor guide]: https://github.com/AGMoller/social-llama/blob/main/CONTRIBUTING.md\n[command-line reference]: https://social-llama.readthedocs.io/en/latest/usage.html\n",
    'author': 'Anders Giovanni Møller',
    'author_email': 'andersgiovanni@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/AGMoller/social-llama',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.11.0,<3.12.0',
}


setup(**setup_kwargs)
