from setuptools import setup, find_packages

setup(
    name='element_python_package',
    version='0.2.11',
    packages=find_packages(),
    install_requires=[
        'scikit-learn',
        'seaborn',
        'matplotlib',
        'pandas',
        'numpy',
    ],
    author='Sharadind Peddiraju',
    author_email='sharadind.pv@gmail.com',
    description='This package contains a collection of tools to help build refined models using techniques from weak supervision. It includes tool from data cleaning to model performance and model report generation.',
)