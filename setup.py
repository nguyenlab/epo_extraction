from setuptools import setup

setup(
    name='epo_extraction',
    version='0.1',
    packages=['epo_extraction', 'epo_extraction.utils', 'epo_extraction.annotation', 'epo_extraction.data_model',
              'epo_extraction.data_access'],
    url='',
    license='',
    author='Danilo S. Carvalho',
    author_email='danilo@jaist.ac.jp',
    description='',
    install_requires=[
        'pymongo',
        'saf',
        'nltk'
    ]
)
