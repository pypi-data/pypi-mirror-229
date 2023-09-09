# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['atom']

package_data = \
{'': ['*']}

install_requires = \
['torch']

setup_kwargs = {
    'name': 'atom-torch',
    'version': '0.0.2',
    'description': 'atom - Pytorch',
    'long_description': '[![Multi-Modality](agorabanner.png)](https://discord.gg/qUtxnK2NMf)\n\n# Atom\nAtom is a finetuned LLAMA to create better LLMS through Pytorch Data!\n\n\n\n\n## Installation\n\nYou can install the package using pip\n\n```python\ngit clone https://github.com/jquesnelle/yarn\ncd Atom\npip install -e .\n```\n\n### Training\n\nTo train the models, run `accelerate config` and enable DeepSpeed acceleration. `deepspeed/zero3.json` was the configuration file used for training.\n\n```sh\n# ./train.sh\n```\n\nThe tokenized training data is available on [Hugging Face](https://huggingface.co/datasets/emozilla/pg_books-tokenized-bos-eos-chunked-65536) and was derived from the [pg19](https://huggingface.co/datasets/emozilla/pg19) dataset.\n\n### Evaluation\n\nTo reproduce the evaluations, install [lm-evaluation-harness](https://github.com/EleutherAI/lm-evaluation-harness) with `pip install git+https://github.com/EleutherAI/lm-evaluation-harness` and then run the two provided scripts.\n\n```sh\n# ./eval.sh\n# ./eval-harness.sh\n```\n\n### Citation\n\n```\n@misc{peng2023yarn,\n      title={YaRN: Efficient Context Window Extension of Large Language Models}, \n      author={Bowen Peng and Jeffrey Quesnelle and Honglu Fan and Enrico Shippole},\n      year={2023},\n      eprint={2309.00071},\n      archivePrefix={arXiv},\n      primaryClass={cs.CL}\n}\n```',
    'author': 'Kye Gomez',
    'author_email': 'kye@apac.ai',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/kyegomez/atom',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
