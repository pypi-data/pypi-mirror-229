# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['SEScore2',
 'SEScore2.inference',
 'SEScore2.preprocess',
 'SEScore2.syn_data',
 'SEScore2.train']

package_data = \
{'': ['*']}

install_requires = \
['transformers',
'sentencepiece',
'protobuf==3.20.*',
'python-snappy',
'pandas',
'nvitop',
'click',
'datasets',
'wandb',
'scipy',
'absl-py',
'torch',
'torchvision',
'torchaudio']

setup_kwargs = {
    'name': 'SEScore2',
    'version': '0.0.9',
    'description': 'SEScore2: Retrieval Augmented Pretraining for Text Generation Evaluation',
    'long_description': 'SESCORE2, is a SSL method to train a metric for general text generation tasks without human ratings. We develop a technique to synthesize candidate sentences with varying levels of mistakes for training. To make these self-constructed samples realistic, we introduce retrieval augmented synthesis on anchor text; It outperforms SEScore in four text generation tasks with three languages (The overall kendall correlation improves 14.3%).'
    ,
    'author': 'Wenda Xu, Xian Qian, Mingxuan Wang, Lei Li, William Yang Wang',
    'author_email': 'wendaxu@ucsb.edu',
    'maintainer': 'Wenda Xu, Zihan Ma',
    'maintainer_email': 'zihan_ma@ucsb.edu',
    'url': 'https://github.com/xu1998hz/SEScore2_archive',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8.0,<4.0.0',
}


setup(**setup_kwargs)
