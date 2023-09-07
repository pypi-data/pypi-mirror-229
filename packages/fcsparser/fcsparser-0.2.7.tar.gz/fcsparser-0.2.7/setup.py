# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fcsparser', 'fcsparser.tests']

package_data = \
{'': ['*'],
 'fcsparser.tests': ['data/FlowCytometers/Cytek_xP5/*',
                     'data/FlowCytometers/FACSCaliburHTS/*',
                     'data/FlowCytometers/FACS_Diva/*',
                     'data/FlowCytometers/Fortessa/*',
                     'data/FlowCytometers/GuavaMuse/*',
                     'data/FlowCytometers/HTS_BD_LSR-II/*',
                     'data/FlowCytometers/MiltenyiBiotec/FCS2.0/*',
                     'data/FlowCytometers/MiltenyiBiotec/FCS3.0/*',
                     'data/FlowCytometers/MiltenyiBiotec/FCS3.1/*',
                     'data/FlowCytometers/corrupted/*',
                     'data/FlowCytometers/cyflow_cube_8/*',
                     'data/FlowCytometers/cytek-nl-2000/*',
                     'data/FlowCytometers/fake_bitmask_error/*',
                     'data/FlowCytometers/fake_large_fcs/*']}

install_requires = \
['numpy>=1,<2', 'pandas>=1.5.3,<2.0.0']

setup_kwargs = {
    'name': 'fcsparser',
    'version': '0.2.7',
    'description': 'A python package for reading raw fcs files',
    'long_description': 'FCSParser\n=================\n\n\nfcsparser is a python package for reading fcs files. \n\n.. image:: https://github.com/eyurtsev/kor/actions/workflows/test.yml/badge.svg?branch=main&event=push   \n   :target: https://github.com/eyurtsev/kor/actions/workflows/test.yml\n   :alt: Unit Tests\n\nInstall\n==================\n\n    $ pip install fcsparser\n    \nor\n    \n    $ conda install -c bioconda fcsparser\n\nUsing\n==================\n\n    >>> import fcsparser\n    >>> path = fcsparser.test_sample_path\n    >>> meta, data = fcsparser.parse(path, reformat_meta=True)\n\nA more detailed example can be found here: https://github.com/eyurtsev/fcsparser/blob/master/doc/fcsparser_example.ipynb\n\nFeatures\n===================\n\n- **python**: 3.8, 3.9, 3.10, 3.11\n- **FCS Formats**: Supports FCS 2.0, 3.0, and 3.1\n- **FCS Machines**: BD FACSCalibur, BD LSRFortessa, BD LSR-II, MiltenyiBiotec MACSQuant VYB, Sony SH800\n\nContributing\n=================\n\nPull requests are greatly appreciated. Missing features include:\n\n1. the ability to apply compensation.\n2. a set of transformations (hlog, logicle, etc.) that can be applied.\n\nAlso fcs files from more devices and more formats are greatly appreciated, especially if the parser fails for them!\n\nResources\n==================\n\n- **Documentation:** https://github.com/eyurtsev/fcsparser\n- **Source Repository:** https://github.com/eyurtsev/fcsparser\n- **Comments or questions:** https://github.com/eyurtsev/fcsparser/issues\n\nLICENSE\n===================\n\nThe MIT License (MIT)\n\nCopyright (c) 2013-2023 Eugene Yurtsev\n\nPermission is hereby granted, free of charge, to any person obtaining a copy\nof this software and associated documentation files (the "Software"), to deal\nin the Software without restriction, including without limitation the rights\nto use, copy, modify, merge, publish, distribute, sublicense, and/or sell\ncopies of the Software, and to permit persons to whom the Software is\nfurnished to do so, subject to the following conditions:\n\nThe above copyright notice and this permission notice shall be included in\nall copies or substantial portions of the Software.\n\nTHE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\nIMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\nFITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\nAUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\nLIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\nOUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN\nTHE SOFTWARE.\n',
    'author': 'Eugene Yurtsev',
    'author_email': 'eyurtsev@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://www.github.com/eyurtsev/kor',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8.0,<4.0.0',
}


setup(**setup_kwargs)
