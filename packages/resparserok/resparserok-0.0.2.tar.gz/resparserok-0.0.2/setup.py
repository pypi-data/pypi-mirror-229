from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

setup(
    name='resparserok',
    version='0.0.2',
    description='A simple resume parser used for extracting information from resumes, compatible with python 3.10',
    url='https://github.com/sinmentis/pyresparser-py3.10',
    author='maman',
    license='GPL-3.0',
    include_package_data=True,
    packages=find_packages(),
    install_requires=['attrs==23.1.0', 'blis==0.7.8', 'catalogue==2.0.6', 'certifi==2023.7.22', 'cffi==1.15.1', 'chardet==5.2.0', 'charset-normalizer==3.2.0', 'click==8.1.7', 'confection==0.1.1', 'cryptography==41.0.3', 'cymem==2.0.7', 'docx2txt==0.8', 'idna==3.4', 'Jinja2==3.1.2', 'joblib==1.3.2', 'jsonschema==4.19.0', 'langcodes==3.3.0', 'MarkupSafe==2.1.3', 'murmurhash==1.0.9',
                      'nltk==3.8.1', 'numpy==1.26.0b1', 'packaging==23.1', 'pandas==2.1.0', 'pathy==0.10.2', 'pdfminer.six==20221105', 'preshed==3.0.5', 'pycparser==2.21', 'pycryptodome==3.18.0', 'pydantic==1.10.12', 'pyresparser==1.0.6', 'pyrsistent==0.19.3', 'python-dateutil==2.8.2', 'pytz==2023.3', 'regex==2023.8.8', 'requests==2.31.0', 'six==1.16.0', 'smart-open==6.3.0', 'sortedcontainers==2.4.0', 'spacy==3.6.1', 'spacy-legacy==3.0.12', 'spacy-loggers==1.0.4', 'srsly==2.4.7', 'thinc==8.1.12', 'tqdm==4.66.1', 'typer==0.9.0', 'typing_extensions==4.7.1', 'urllib3==2.0.4', 'wasabi==1.1.2'],
    zip_safe=False,
    entry_points={
        'console_scripts': ['pyresparser=pyresparser.command_line:main'],
    }
)
