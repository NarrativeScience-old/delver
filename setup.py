import setuptools
import os

setuptools.setup(
    name='delver',
    version='0.0.2',
    maintainer='Alex Sippel',
    maintainer_email='asippel@narrativescience.com',
    url='https://github.com/NarrativeScience/delver',
    package_dir={'': 'src'},
    packages=setuptools.find_packages('src'),
    provides=setuptools.find_packages('src'),
    entry_points={
        'console_scripts': [
            'delve = delver.delve:main'
        ]
    }
)
