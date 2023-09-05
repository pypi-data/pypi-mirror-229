# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cornflakes',
 'cornflakes.builder',
 'cornflakes.cli',
 'cornflakes.common',
 'cornflakes.decorator',
 'cornflakes.decorator.click',
 'cornflakes.decorator.click.helper',
 'cornflakes.decorator.click.options',
 'cornflakes.decorator.click.rich',
 'cornflakes.decorator.dataclasses',
 'cornflakes.decorator.dataclasses.config',
 'cornflakes.decorator.dataclasses.validator',
 'cornflakes.decorator.datalite',
 'cornflakes.logging',
 'cornflakes.packaging',
 'cornflakes.parser']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0.1,<7.0.0',
 'click>=8.1.3,<9.0.0',
 'rich-rst>=1.1.7,<2.0.0',
 'rich==13.5.2',
 'toml>=0.10.2,<0.11.0',
 'typeguard>=4.1.3,<5.0.0',
 'typing-extensions>=4.7.1,<5.0.0',
 'validators>=0.20,<0.23']

entry_points = \
{'console_scripts': ['cornflakes = cornflakes.__main__:main']}

setup_kwargs = {
    'name': 'cornflakes',
    'version': '3.3.13',
    'description': 'Create generic any easy way to manage Configs for your project',
    'long_description': '## <img src="https://github.com/semmjon/cornflakes/blob/main/assets/cornflakes.png?raw=true" alt="cornflakes logo" width="400" height="400"/>\n\n![PyPI](https://img.shields.io/pypi/v/cornflakes.svg)\n![Python Version](https://img.shields.io/pypi/pyversions/cornflakes)\n![License](https://img.shields.io/github/license/semmjon/cornflakes)\n![Read the Docs](https://github.com/sgeist-ionos/cornflakes/actions/workflows/build_package.yml/badge.svg?branch=main)\n![Build](https://github.com/semmjon/cornflakes/workflows/Build%20cornflakes%20Package/badge.svg)\n![Tests](https://github.com/sgeist-ionos/cornflakes/actions/workflows/run_tests.yml/badge.svg?branch=main)\n![Codecov](https://codecov.io/gh/sgeist-ionos/cornflakes/graph/badge.svg?token=FY72EIXI82)\n\n```bash\npip install cornflakes\n```\n\n```bash\npip install git+https://github.com/semmjon/cornflakes\n```\n\n> :warning: **Warning**: Please be careful when using this Python module. Currently, it is only developed / tested by me, which is why it has a high update / change rate. I\'m actually trying to be compatible with implementations, but I can\'t guarantee this at the moment. The module is currently still in a beta state and is not recommended for productive use.\n\n---\n\n## Information\n\nThe Python module "cornflakes" was started as a hobby project and offers an alternative to Pydantic for managing configurations and data structures. It allows creating generic and easy to manage configurations for your project. Unlike Pydantic, which is based on inheritance, "cornflakes" uses a decorator (similar to dataclass) to map data structures.\n\n### Short Term RoadMap\n\n-   Add autocompletion support for click CLI (automatically)\n-   Change Code Annotations\n    -   remove Any annotations if possible\n    -   change Protocol Annotations to specific type classes\n-   Enrich json methods\n-   Fix / Test the to\\_<file-format> Methods (specially yaml)\n\n---\n\n## Development\n\n### Prerequisites\n\n-   A compiler with C++17 support\n-   Pip 10+ or CMake >= 3.4\n-   Python 3.8+\n-   doxygen\n-   cppcheck\n-   clang-tools-extra or clang-tidy\n\n### Commands\n\nClone this repository and pip install. Note the `--recursive` option which is needed for the pybind11 submodule:\n\n```bash\ngit clone --recursive https://gitlab.blubblub.tech/sgeist/cornflakes.git\n```\n\nInstall the package using makefiles:\n\n```bash\nmake install\n```\n\nBuild dist using makefiles:\n\n```bash\nmake dist\n```\n\nRun tests (pytest) using makefiles:\n\n```bash\nmake test\n```\n\nRun all tests using makefiles:\n\n```bash\nmake test-all\n```\n\nRun lint using makefiles:\n\n```bash\nmake lint\n```\n\nCreate dev venv:\n\n```bash\npython -m venv .venv\nsource .venv/bin/activate\npip install ninja pre-commit poetry\n```\n\nInstall pre-commit:\n\n```bash\npre-commit install\n```\n\nUpdate pre-commit:\n\n```bash\npre-commit update -a\n```\n\nRun pre-commit:\n\n```bash\npre-commit run -a\n```\n',
    'author': 'Semjon Geist',
    'author_email': 'semjon.geist@ionos.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/sgeist/cornflakes',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}
from build import *
build(setup_kwargs)

setup(**setup_kwargs)
