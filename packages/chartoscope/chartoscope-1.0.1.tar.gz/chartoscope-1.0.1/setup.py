from setuptools import setup

setup(
    name='chartoscope',
    version='1.0.1',
    packages=['chartoscope'],
    package_data={'chartoscope': ['lib/libchartoscope.so']},
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description=open('README.txt').read(),
)
