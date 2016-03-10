import setuptools
import os

# This will add the __version__ to the globals
execfile('src/__init__.py')

setuptools.setup(
    name='data_explorer',
    version=__version__,
    package_dir={'': 'src'},
    packages=setuptools.find_packages('src'),
    provides=setuptools.find_packages('src'),
    entry_points={
        'console_scripts': ['explore = explore:main']
    }
)
