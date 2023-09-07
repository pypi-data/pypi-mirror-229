# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['simplelinkedin', 'simplelinkedin.crons', 'simplelinkedin.scripts']

package_data = \
{'': ['*'], 'simplelinkedin': ['log_config/*']}

install_requires = \
['PyYAML>=6.0.1,<7.0.0',
 'django-environ>=0.11.1,<0.12.0',
 'python-dotenv>=1.0.0,<2.0.0',
 'selenium>=4.12.0,<5.0.0',
 'simpleselenium==0.4.1']

setup_kwargs = {
    'name': 'simplelinkedin',
    'version': '1.0.0',
    'description': 'Python package to automate activities on LinkedIn.',
    'long_description': '# LinkedIn\n\nPython package to automate some usual tasks performed on social-networking site LinkedIn.\n\n### What can you do?\n\nThe package helps to do the followings [with a number of improvements planned in future]\n\n- Login to LinkedIn\n- Send connection requests\n    - Filter by minimum and maximum number of mutual connections\n    - Filter by kinds of users (preferred and not preferred)\n    - Maximum number of requests to be sent\n    - Optionally, view the profile of those sending request to\n- Accept connection requests\n- Delete/Withdraw sent connection requests depending on how old they are\n- Run smart follow-unfollow\n    - Delete sent requests older than 14 days\n    - Follow the maximum number of people possible for the day (based on LinkedIn\'s weekly limit)\n    - Accept all pending requests\n- Run all of these in the background mode without affecting your usual work\n\nNote: The package has been tested on macOS and is expected to work on Linux/Unix environments as well. Raise an issue/PR\nif you encounter any issue while running the scripts.\n\n### Getting Started\n\nInstall file from PyPi\n\n```bash\npip install simplelinkedin\n```\n\nThe best way to run and test the package for your needs is to use `sample_script.py` like below. Start with running your\npackage by supplying `LINKEDIN_BROWSER_HEADLESS=0` and if everything runs well, you can set the same back\nto `LINKEDIN_BROWSER_HEADLESS=1` to run your script in the background.\n\n```python\nfrom simplelinkedin.linkedin import LinkedIn\n\nsettings = {\n    "LINKEDIN_USER": "<username>",\n    "LINKEDIN_PASSWORD": "<password>",\n    "LINKEDIN_BROWSER": "Chrome",\n    "LINKEDIN_BROWSER_HEADLESS": 0,\n    "LINKEDIN_PREFERRED_USER": "/path/to/preferred/user/text_doc.text",\n    "LINKEDIN_NOT_PREFERRED_USER": "/path/to/not/preferred/user/text_doc.text",\n}\n\nwith LinkedIn(\n        username=settings.get("LINKEDIN_USER"),\n        password=settings.get("LINKEDIN_PASSWORD"),\n        browser=settings.get("LINKEDIN_BROWSER"),\n        headless=bool(settings.get("LINKEDIN_BROWSER_HEADLESS")),\n) as ln:\n    # do all the steps manually\n    ln.login()\n    ln.remove_sent_invitations(older_than_days=14)\n\n    ln.send_invitations(\n        max_invitation=max(ln.WEEKLY_MAX_INVITATION - ln.invitations_sent_last_week, 0),\n        min_mutual=10,\n        max_mutual=450,\n        preferred_users=["Quant"],  # file_path or list of features\n        not_preferred_users=["Sportsman"],  # file_path or list of features\n        view_profile=True,  # (recommended) view profile of users you sent connection request to\n    )\n\n    ln.accept_invitations()\n\n    # OR\n    # run smart follow-unfollow method which essentially does the same thing as\n    # all the above steps\n    ln.smart_follow_unfollow(\n        users_preferred=settings.get("LINKEDIN_PREFERRED_USER") or [],\n        users_not_preferred=settings.get("LINKEDIN_NOT_PREFERRED_USER") or [],\n    )\n```\n\nAlternatively, you can go the command line way, like below.\n\n    > python -m simplelinkedin -h\n\n    usage: simplelinkedin [-h] [--env ENV] [--email EMAIL] [--password PASSWORD]\n                          [--browser BROWSER] [--headless] [--preferred PREFERRED]\n                          [--notpreferred NOTPREFERRED]\n\n    options:\n      -h, --help            show this help message and exit\n      --env ENV             Linkedin environment file\n      --email EMAIL         Email of linkedin user\n      --password PASSWORD   Password of linkedin user\n      --browser BROWSER     Browser used for linkedin\n      --headless            Whether to run headless\n      --preferred PREFERRED\n                            Path to file containing preferred users\n                            characteristics\n      --notpreferred NOTPREFERRED\n                            Path to file containing characteristics of not\n                            preferred users\n\nStart with the following commands.\nUse `example.env` file as reference while setting `.env` values.\n\n    python linkedin.py --env .env\n    python linkedin.py --email abc@gmail.com --password $3cRET --browser Chrome --preferred data/users_preferred.txt --notpreferred data/users_not_preferred.txt\n\n\n`example.env`\n\n    LINKEDIN_USER=\n    LINKEDIN_PASSWORD=\n    LINKEDIN_BROWSER=Chrome\n    LINKEDIN_BROWSER_HEADLESS=1\n    LINKEDIN_PREFERRED_USER=data/users_preferred.txt\n    LINKEDIN_NOT_PREFERRED_USER=data/users_not_preferred.txt\n\n\n### Extras\n\nThis package makes use of another package named [simpleselenium](https://github.com/inquilabee/simpleselenium). Do check that out.\n\n### TODOS\n\n- improve documentation\n- Include Tests\n',
    'author': 'Vishal Kumar Mishra',
    'author_email': 'vishal.k.mishra2@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/TheConfused/LinkedIn',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
