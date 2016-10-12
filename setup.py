import setuptools
import os

setuptools.setup(
    name='delver',
    version='0.0.2',
    maintainer='Alex Sippel',
    maintainer_email='asippel@narrativescience.com',
    url='https://github.com/NarrativeScience/delver',
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4'
    ],
    package_dir={'': 'src'},
    packages=setuptools.find_packages('src'),
    provides=setuptools.find_packages('src'),
    install_requires=open('requirements.txt').readlines(),
    entry_points={
        'console_scripts': [
            'delve = delver.delve:main'
        ]
    }
)
