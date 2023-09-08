from setuptools import setup

with open("README.md", 'r') as f:
    long_description = f.read()

setup(
    name = 'princurve',
    version = '0.0.1',
    license = "MIT",
    description = "A package for fitting principal curves in Python",
    author="https://github.com/wangzichenbioinformatics",
    author_email="wch_bioinformatics@163.com",
    url = 'https://github.com/wangzichenbioinformatics/princurve', 
    packages = ["princurve"],
    long_description = long_description,
    long_description_content_type='text/markdown',
    install_requires = ['numpy',
                        'matplotlib',
                        'scipy',
                        'keras',
                        'tensorflow',
                        ],
)