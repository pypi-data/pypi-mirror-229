# python setup.py sdist && twine upload/yml-api-0.0.1.tar.gz

import os
from setuptools import find_packages, setup

with open('api/requirements.txt') as file:
    requirements = file.read().strip().splitlines()
print(requirements)

setup(
    name='yml-api',
    version='0.0.2',
    packages=find_packages(exclude=('pnp', 'pnp.*')),
    install_requires=requirements,
    extras_require={
        'dev': [],
        'production': [],
    },
    include_package_data=True,
    license='BSD License',
    description='API generator based on yml file',
    long_description='',
    url='https://github.com/brenokcc',
    author='Breno Silva',
    author_email='brenokcc@yahoo.com.br',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
