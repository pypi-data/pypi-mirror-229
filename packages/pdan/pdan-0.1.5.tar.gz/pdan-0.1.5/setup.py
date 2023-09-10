# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pdan']

package_data = \
{'': ['*']}

install_requires = \
['gon>=5.0.0,<6.0.0', 'matplotlib>=3.6.2,<4.0.0']

setup_kwargs = {
    'name': 'pdan',
    'version': '0.1.5',
    'description': '',
    'long_description': 'pdan\n===========\n\n\n[![](https://travis-ci.org/LostFan123/pdan.svg?branch=master)](https://travis-ci.org/LostFan123/pdan "Travis CI")\n[![](https://dev.azure.com/skorobogatov/pdan/_apis/build/status/LostFan123.pdan?branchName=master)](https://dev.azure.com/skorobogatov/pdan/_build/latest?definitionId=2&branchName=master "Azure Pipelines")\n[![](https://codecov.io/gh/LostFan123/pdan/branch/master/graph/badge.svg)](https://codecov.io/gh/LostFan123/pdan "Codecov")\n[![](https://img.shields.io/github/license/LostFan123/pdan.svg)](https://github.com/LostFan123/pdan/blob/master/LICENSE "License")\n[![](https://badge.fury.io/py/pdan.svg)](https://badge.fury.io/py/pdan "PyPI")\n\nIn what follows\n- `python` is an alias for `python3.8` or any later\nversion (`python3.9` and so on).\n\nInstallation\n------------\n\nInstall the latest `pip` & `setuptools` packages versions:\n  ```bash\n  python -m pip install --upgrade pip setuptools\n  ```\n\n### User\n\nDownload and install the latest stable version from `PyPI` repository:\n  ```bash\n  python -m pip install --upgrade pdan\n  ```\n\n### Developer\n\nDownload the latest version from `GitHub` repository\n```bash\ngit clone https://github.com/LostFan123/pdan.git\ncd pdan\n```\n\nInstall dependencies:\n  ```bash\n  poetry install\n  ```\n\nUsage\n-----------\n```python\n>>> from pdan import minimizing_split, Contour, Point, Polygon\n>>> contour = Contour([Point(0, 0), Point(1, 0), Point(1, 1), Point(0, 1)])\n>>> part, other = minimizing_split(contour, 0.5, key=lambda x, y: x.length)\n>>> assert Polygon(part).area == Polygon(other).area == 0.5\n```\n\nDevelopment\n-----------\n\n### Bumping version\n\n#### Preparation\n\nInstall\n[bump2version](https://github.com/c4urself/bump2version#installation).\n\n#### Pre-release\n\nChoose which version number category to bump following [semver\nspecification](http://semver.org/).\n\nTest bumping version\n```bash\nbump2version --dry-run --verbose $CATEGORY\n```\n\nwhere `$CATEGORY` is the target version number category name, possible\nvalues are `patch`/`minor`/`major`.\n\nBump version\n```bash\nbump2version --verbose $CATEGORY\n```\n\nThis will set version to `major.minor.patch-alpha`. \n\n#### Release\n\nTest bumping version\n```bash\nbump2version --dry-run --verbose release\n```\n\nBump version\n```bash\nbump2version --verbose release\n```\n\nThis will set version to `major.minor.patch`.\n\n#### Notes\n\nTo avoid inconsistency between branches and pull requests,\nbumping version should be merged into `master` branch \nas separate pull request.\n\n### Running tests\n\nPlain:\n  ```bash\n  pytest\n  ```\n\nInside `Docker` container:\n  ```bash\n  docker-compose --file docker-compose.cpython.yml up\n  ```\n\n`Bash` script (e.g. can be used in `Git` hooks):\n  ```bash\n  ./run-tests.sh\n  ```\n  or\n  ```bash\n  ./run-tests.sh cpython\n  ```\n\n`PowerShell` script (e.g. can be used in `Git` hooks):\n  ```powershell\n  .\\run-tests.ps1\n  ```\n  or\n  ```powershell\n  .\\run-tests.ps1 cpython\n  ```\n',
    'author': 'GeorgySk',
    'author_email': 'skorobogatov@phystech.edu',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
