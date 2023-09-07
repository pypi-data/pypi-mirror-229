import os
from setuptools import find_packages, setup

root_dir = os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir))

print(root_dir)

with open(os.path.join(root_dir, 'requirements.txt')) as file:
    requirements = file.read().strip().splitlines()

os.chdir(root_dir)

setup(
    name='yml-api',
    version='0.0.1',
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
