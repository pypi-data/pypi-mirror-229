from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as file:
    long_description = file.read()

setup(
    name='jupyter-swi-prolog',
    version='1.0.2.1',
    author='Eric Tröbs',
    author_email='eric.troebs@tu-ilmenau.de',
    description='a basic wrapper kernel for SWI-Prolog',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/erictroebs/jupyter-swi-prolog',
    project_urls={
        'Bug Tracker': 'https://github.com/erictroebs/jupyter-swi-prolog/issues',
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    python_requires='>=3.7',
    install_requires=[
        'jupyter',
        'swiplserver~=1.0.2'
    ],
    package_data={
        'swi_prolog_kernel': [
            'kernel.json'
        ]
    },
    include_package_data=True
)
