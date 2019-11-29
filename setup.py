import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-tsugi',
    version='0.1.12',
    packages=find_packages(),
    include_package_data=True,
    license='Apache License',  # example license
    description='Library code to help write Python Tools that use the Tsugi library to integrate into Learning Management Systems.',
    long_description=README,
    url='https://github.com/tsugiproject/django-tsugi.git',
    author='Charles Severance (Dr. Chuck)',
    author_email='drchuck@learnxp.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.1',  # replace "X.Y" as appropriate
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License', 
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=[
        'cryptography>=2.5',
        'Django>=2.1.7',
        'PyJWT>=1.7.1',
        'requests>=2.17.3',
        'jwcrypto>=0.6.0'
    ],
)

