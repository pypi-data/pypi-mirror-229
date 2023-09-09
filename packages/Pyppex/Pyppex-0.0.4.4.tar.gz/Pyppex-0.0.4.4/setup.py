from setuptools import setup, find_packages

setup(
    name='Pyppex',
    version='0.0.4.4',
    description='All sorts of utilities designed to ease developers productivity.',
    license='MIT License',
    author='n0t10n',
    author_email='0ts.notion@gmail.com',
    maintainer='Marcos',
    maintainer_email='0ts.notion@gmail.com',
    packages=find_packages(),
    requires=['multiprocessing', 'numpy']
)