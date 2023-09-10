# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['git_user23']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'git-user23',
    'version': '0.0.3',
    'description': 'A Python library for GitHub API integration. Retrieve user info, repositories, and more. Simplify GitHub-related tasks effortlessly.',
    'long_description': '# git-user\n\n### Purpose of the Package\n\nA Python library for GitHub API integration. Retrieve user info, repositories, and more. Simplify GitHub-related tasks effortlessly.\n\n### Features\n\n- ------List of functions------\n  - format_username(username)\n  - confirm_username(username)\n  - get_response(username)\n  - full_name(username)\n  - twitter(username)\n  - repos(username)\n  - bio(username)\n  - location(username)\n  - repo_count(username)\n  - followers_count(username)\n  - following_count(username)\n  - joined_date(username)\n  - confirm_token(username, token)\n  - create_repo(username, token, repo_name)\n\n### Dependencies\n\nPython >3\nRequest `pip install requests`\n\n### Getting Started\n\nThe package can be found on pypi hence you can install it using pip\n\n### Installation\n\n```bash\npip install git_user23\n```\n\n# How to use\n\n## List of functions\n\nformat_username(username)\nThis function removes leading and trailing spaces from the given username.\n\n```python\n>>> from git_user23 import *\n>>> format_username("           samuelogboye")\n\'samuelogboye\'\n>>> format_username("     samuelogboye        ")\n\'samuelogboye\'\n```\n\nconfirm_username(username)\nChecks if a given username is valid on GitHub.\n\n```python\n>>> from git_user23 import *\n>>> confirm_username("samuelogboye")\nTrue\n>>> confirm_username("samuelogboy")\nFalse\n```\n\nget_response(username)\nRetrieves all user information from GitHub API and returns it as a dictionary.\n\n```python\n>>> from git_user23 import *\n>>> get_response("samuelogboye")\ninfo\n```\n\nfull_name(username)\nRetrieves the full name of the user\n\n```python\n>>> from git_user23 import *\n>>> full_name("samuelogboye")\n\'Samuel Ogboye\'\n\n```\n\ntwitter(username)\nRetrieves the twitter username of a user\n\n```python\n>>> from git_user23 import *\n>>> twitter("samuelogboye")\n\'samuel_ogboye\'\n\n```\n\nrepos(username)\nRetrieves a list of all repositories owned by the user.\n\n```python\n>>> from git_user23 import *\n>>> repos("samuelogboye")\nlist of repo\n\n```\n\nbio(username)\nRetrieves the bio of the user\n\n```python\n>>> from git_user23 import *\n>>> bio("samuelogboye")\n\'Software Engineer || Open Source || Technical Writer || C || Python\'\n\n```\n\nlocation(username)\nRetrieves the location of the user.\n\n```python\n>>> from git_user23 import *\n>>> location("samuelogboye")\n\'Nigeria\'\n\n```\n\nrepo_count(username)\nRetrives the count of public repositories owned by the user.\n\n```python\n>>> from git_user23 import *\n>>> repo_count("samuelogboye")\n30\n\n```\n\nfollowers_count(username)\nRetrieves the count of followers of the user.\n\n```python\n>>> from git_user23 import *\n>>> followers_count("samuelogboye")\n75\n\n```\n\nfollowing_count(username)\nRetrieves the count of users that the user is following.\n\n```python\n>>> from git_user23 import *\n>>> following_count("samuelogboye")\n64\n\n```\n\njoined_date(username)\nRetrieves the date when the user joined GitHub.\n\n```python\n>>> from git_user23 import *\n>>> joined_date("samuelogboye")\n\'2023-02-16\'\n\n```\n\nconfirm_token(username, token)\nConfirms if both username and token are valid. Returns True or False\n\n```python\n>>> from git_user23 import *\n>>> confirm_token("samuelogboye", *********)\nFalse\n\n```\n\ncreate_repo(username, token, repo_name)\nCreates a public GitHub repository instantly with a README file and returns True if successful.\n\n```python\n>>> from git_user23 import *\n>>> create_repo("samuelogboye", "******", "testing")\nTrue\n\n```\n\n### Contribution\n\nContributions are welcome\nNotice a bug, let us know. Thanks\n\n### Author\n\n- Main Maintainer: Samuel Ogboye\n- Jesus Saves\n',
    'author': 'Samuel Ogboye',
    'author_email': 'ogboyesam@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/samuelogboye/git-user',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3,<4',
}


setup(**setup_kwargs)
