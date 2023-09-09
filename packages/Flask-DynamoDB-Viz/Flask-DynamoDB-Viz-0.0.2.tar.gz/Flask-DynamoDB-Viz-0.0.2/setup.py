"""
flask-dynamodb-viz
---------------

A flask extension to view dynamodb table records and structure
"""

from setuptools import find_packages, setup

setup(
    name="Flask-DynamoDB-Viz",
    url="https://github.com/djmgit/flask-dynamodb-viz",
    license="",
    author="Deepjyoti Mondal",
    description="Dynamodb extension for Flask",
    download_url="https://github.com/djmgit/flask-dynamodb-viz/archive/refs/tags/v0.0.2.tar.gz",
    long_description=__doc__,
    zip_safe=False,
    keywords = ["Flask", "Python", "Dynamodb", "AWS", "Extension", "Flask-Extension"],
    platforms="any",
    packages=find_packages(),
    install_requires=[
        "requests>=2.0.0",
        "Flask>=1.1.2"
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: System :: Monitoring',
    ],
    version='0.0.2'
)
