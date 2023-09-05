import io
from setuptools import find_packages, setup


def long_description():
    with io.open('README.md', 'r', encoding='utf-8') as f:
        readme = f.read()
    return readme


setup(
    name='xalgorithm',
    version='0.0.1',
    description='My Data Structures and Algorithms Implemented in Python',
    long_description=long_description(),
    long_description_content_type="text/markdown",
    url='https://github.com/keon/algorithms',
    author='Xiang Liu',
    author_email="dennisl@udel.edu",
    license='MIT',
    packages=find_packages(exclude=('tests', 'tests.*')),
    zip_safe=False,
    platforms = ["Linux"]
)