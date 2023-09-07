# python setup.py install

from setuptools import setup, find_packages

setup(
    name='datapeach-cli',
    version='1.0.1',
    py_modules=['datapeachcli', 'analysis_usedecorator'],
    packages=find_packages(),
    include_package_data=True,
    package_data={'datapeach_cli': ['templates/*', 'config.json']},
    install_requires=[
        'click',
        'jinja2',
        'nbformat',
        'nbconvert',
        'pulsar',
        'mysql-connector',
        'pandas',
        'pyyaml',
        'ipython',
        'requests',
        'datapeach_wrapper',
    ],
    entry_points='''
        [console_scripts]
        datapeach=datapeachcli:cli
    ''',
)
