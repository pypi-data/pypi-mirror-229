from setuptools import setup, find_packages
from pathlib import Path

version = '0.0.4.2'

directory = Path(__file__).parent

with open(Path(directory, 'README.md'), 'r') as file:
    if file.readable():
        long_description = file.read()
    else:
        long_description = ''


setup(
    name='yaschedule',
    version=version,
    description='Lib for getting schedule data from Yandex.Rasp API',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/StannisGr/yaschedule',
    author='StannisGr',
    author_email='bvc344@gmail.com',
    license='Apache License 2.0',
    platforms=['any'],
    keywords='yandex, schedule, api, yandex.rasp',
    packages=find_packages(exclude=('tests',)),
    include_package_data=True,
    install_requires=[
    'attrs==23.1.0',
    'cattrs==23.1.2',        
    'certifi>=2021.10.8',
    'charset-normalizer>=2.0.12',
    'exceptiongroup==1.1.3',
    'idna>=3.3',
    'platformdirs==3.10.0',
    'requests>=2.27.1',
    "requests-cache==1.1.0",
    "six==1.16.0",
    "typing_extensions==4.7.1",
    "url-normalize==1.4.3",
    'urllib3>=1.26.9',
    ],
)
