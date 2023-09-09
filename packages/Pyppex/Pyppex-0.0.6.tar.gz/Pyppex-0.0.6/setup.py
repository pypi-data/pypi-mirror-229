from setuptools import setup, find_packages

setup(
    name='Pyppex',
    version='0.0.6',
    description='All sorts of utilities designed to ease developers productivity.',
    url='https://pypi.org/project/Pyppex/',
    license='MIT',
    author='n0t10n',
    author_email='0ts.notion@gmail.com',
    maintainer='Marcos',
    maintainer_email='0ts.notion@gmail.com',
    packages=find_packages(),
    install_requires=['numpy'],
    classifiers=[
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ]
)