from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    author="Rafael Gómez Bermejo",
    author_email="sernn2@gmail.com",
    name="architecture-tools-RafaelGB",
    version='0.0.7',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Topic :: Adaptive Technologies',
		'Operating System :: OS Independent',
      ],
      keywords='architecture wrapper',
      url='https://github.com/RafaelGB/pythonScripts',
    description='Tools for an architecture skeleton',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
          'markdown',
    ],
    python_requires='>=3.6',
    include_package_data=True,
    zip_safe=False
)