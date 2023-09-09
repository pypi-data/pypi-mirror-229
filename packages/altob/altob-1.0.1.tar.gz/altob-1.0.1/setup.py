from setuptools import setup

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='altob',
    version='1.0.1',
    description='Identify frequencies of concerning mutations from aligned reads',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Isaac Ellmen',
    author_email='isaac.ellmen@uwaterloo.ca',
    maintainer='Jenn Knapp',
    maintainer_email='jenn.knapp@uwaterloo.ca',
    packages=['altob'],
    url='https://github.com/Ellmen/altob',
    install_requires=[
        'fire',
        'numpy',
        'pandas',
        'scikit-learn>=0.24',
        'matplotlib',
        'seaborn',
        'pysam',
        'ortools',
    ],
    entry_points={
        'console_scripts': ['altob=altob.command_line:main'],
    }
)
