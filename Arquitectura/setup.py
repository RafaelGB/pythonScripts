"""
from setuptools import setup, find_packages

setup(name='arqTools', version='1.0', packages=find_packages())
"""
from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    author="Rafael Gómez Bermejo",
    author_email="sernn2@gmail.com",
    name="architecture-tools-RafaelGB",
    version='0.0.9',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Topic :: Adaptive Technologies',
      ],
      keywords='architecture wrapper',
      url='https://github.com/RafaelGB/pythonScripts',
    description='Tools for an architecture skeleton',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
          'markdown==3.2.1',
          'dependency-injector==4.5.4',
          'Flask==1.1.1',
          'Flask-Caching==1.9.0',
          'pylint==2.6.0',
          'cachetools==4.0.0',
          'redis==3.4.1',
          'docker==4.2.0',
          'Rx==3.1.0',
          'dash==1.10.0',
          'dash-bootstrap-components==0.9.2',
          'pandas==1.1.5'
    ],
    python_requires='>=3.7',
    include_package_data=True,
    zip_safe=False
)