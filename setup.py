import setuptools
import os

setuptools.setup(
    name='explorer',
    version='0.0.1',
    package_dir={'': 'src'},
    packages=setuptools.find_packages('src'),
    provides=setuptools.find_packages('src'),
    entry_points={
        'console_scripts': [
            'explore = explorer.explore:main'
        ]
    }
)
