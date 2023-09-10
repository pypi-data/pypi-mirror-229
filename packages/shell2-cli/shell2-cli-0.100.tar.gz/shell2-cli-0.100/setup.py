# setup.py

from setuptools import setup, find_packages

setup(
    name='shell2-cli',
    version='0.100',
    packages=find_packages(),
    install_requires=[
        'shell2',
        'prettyprinter',
        'inquirer',
        'rich',
        'prompt_toolkit',
        'colorama',
        'google-cloud-firestore',
        'google-auth',
        'requests',
        'retry',
        'python-slugify',
        'py7zr'
    ],
    entry_points={
        'console_scripts': [
            'shell2_cli_menu = scripts.shell2_cli_menu:main', # i switch the order of these two and it ceases working ... !
            'shell2_cli_live = scripts.shell2_cli_live:main',
            'shell2 = scripts.shell2_cli:main'
        ]
    }

)
