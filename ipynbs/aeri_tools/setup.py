from setuptools import setup, find_packages

setup(
    name='aeri_tools',
    version='0.1',
    packages=find_packages(),
    url='',
    license='',
    author='cphillips',
    author_email='codaphillips@gmail.com',
    description='',
    install_requires=[
        'pandas',
        'numpy',
        'scipy',
        'quantities',
        'netCDF4',
        'dmv'
    ],
)
