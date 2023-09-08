# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['arraylib']

package_data = \
{'': ['*']}

install_requires = \
['biopython>=1.79',
 'click>=8.1.3',
 'numba>=0.55.2',
 'numpy>=1.22.4',
 'pandas>=1.4.2',
 'pytest',
 'scikit-learn>=1.1.1',
 'scipy>=1.8.1',
 'sphinxcontrib-bibtex>=2.5.0,<3.0.0']

extras_require = \
{'docs': ['Sphinx==4.2.0',
          'sphinx-rtd-theme==1.0.0',
          'sphinxcontrib-napoleon==0.7',
          'nbsphinx==0.8.9'],
 'notebook': ['jupyter']}

entry_points = \
{'console_scripts': ['arraylib-deconvolve = arraylib.main:deconvolve',
                     'arraylib-deconvolve_validation = '
                     'arraylib.main:deconvolve_validation',
                     'arraylib-run = arraylib.main:run',
                     'arraylib-run_on_barcodes = '
                     'arraylib.main:run_on_barcodes']}

setup_kwargs = {
    'name': 'arraylib-solve',
    'version': '0.31.0',
    'description': 'Tool to computationally deconvolve combinatorially pooled arrayed random mutagenesis libraries',
    'long_description': '# arraylib-solve\n\n# Introduction\n\n`arraylib-solve` is a tool to deconvolve combinatorially pooled arrayed random mutagenesis libraries (e.g. by transposon mutagenesis). In a typical experiment generating arrayed mutagenesis libraries, first a pooled version of the library is created and arrayed on a grid of well plates. To infer the identities of each mutant on the well plate, wells are pooled in combinatorial manner such that each mutant appears in a unique combination of pools. The pools are then sequenced using NGS and sequenced reads are stored in individual fastq files per pool. `arraylib-solve` deconvolves the pools and returns summaries stating the identity and location of each mutant on the original well grid. The package is based on the approach described in [[1]](#1).\n\n# Installation\n\nTo install `arraylib` first create `Python 3.8` environment e.g. by\n\n```\nconda create --name arraylib-env python=3.8\nconda activate arraylib-env\n```\n\nand install the package using \n\n```\npip install arraylib-solve\n```\n\n`arraylib-solve` uses bowtie2 [[2]](#2) to align reads to the reference genome. Please ensure that bowtie2 is installed in your environment by running:\n\n```\nconda install -c bioconda bowtie2\n```\n\n\n# How to run `arraylib`\n\nA detailed manual how to run `arraylib` interactively and from the command line can be found here https://tcapraz.github.io/arraylib/index.html.\n\n# References\n<a id="1">[1]</a> \nBaym, M., Shaket, L., Anzai, I.A., Adesina, O. and Barstow, B., 2016. Rapid construction of a whole-genome transposon insertion collection for Shewanella oneidensis by Knockout Sudoku. Nature communications, 7(1), p.13270.\\\n<a id="2">[2]</a> \nLangmead, B. and Salzberg, S.L., 2012. Fast gapped-read alignment with Bowtie 2. Nature methods, 9(4), pp.357-359.\n\n',
    'author': 'capraz',
    'author_email': 'tuemayc@hotmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8.1,<3.11',
}


setup(**setup_kwargs)
