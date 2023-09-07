# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['infinite']

package_data = \
{'': ['*']}

install_requires = \
['torch']

setup_kwargs = {
    'name': 'lm-infinite',
    'version': '0.0.2',
    'description': 'Paper - Pytorch',
    'long_description': '[![Multi-Modality](agorabanner.png)](https://discord.gg/qUtxnK2NMf)\n\n# LM-INFINITE: SIMPLE ON-THE-FLY LENGTH GENERALIZATION FOR LARGE LANGUAGE MODELS\n\nLM-Infinite is a solution proposed by Chi Han, Qifan Wang, Wenhan Xiong, Yu Chen, Heng Ji, and Sinong Wang to address the length generalization failure of Large Language Models (LLMs) on long sequences. LLMs, such as Transformer-based models, have shown impressive performance in various domains but struggle when it comes to longer reasoning processes or understanding larger contexts. Current pre-training schemes truncate training sequences to a fixed length, and even with relative positional encoding, LLMs struggle to generate coherent texts or perform downstream tasks after longer contexts.\n\nThe authors investigate the main out-of-distribution factors contributing to this problem and propose LM-Infinite as an efficient solution. LM-Infinite only requires a Λ-shaped attention mask and a distance limit, without any parameter updates or learning. It can be applied to different LLMs using relative-position encoding methods. LM-Infinite demonstrates consistent fluency and generation quality for sequences as long as 32k tokens on datasets like ArXiv and OpenWebText2, with a decoding speedup of 2.72x. Furthermore, it continues to perform well on inputs much longer than training lengths in downstream tasks like passkey retrieval, where vanilla models fail immediately.\n\n[Paper Link](https://arxiv.org/pdf/2308.16137.pdf)\n\n---\n\n# Appreciation\n* Lucidrains\n* Agorians\n\n\n\n# Install\n`pip install lm-infinite`\n\n# Usage\n```python\nimport torch\nfrom infinite.main import LMInfinite\n\nd_model = 512\nseq_len = 100\nn_global = 100\nl_pretrain = 50\n\n\n#sample\nq = torch.randn(1, seq_len, d_model)\nk = torch.randn(1, seq_len, d_model)\nv = torch.randn(1, seq_len, d_model)\n\n\n#llm infinite mode\nmodel = LMInfinite(\n    d_model,\n    n_global,\n    l_pretrain\n)\n\n#forwad pass\noutput = model(q, k, v)\nprint(output.shape)\n```\n# Architecture\n\n# Todo\n\n\n# License\nMIT\n\n# Citations\n```latex\n@misc{2308.16137,\nAuthor = {Chi Han and Qifan Wang and Wenhan Xiong and Yu Chen and Heng Ji and Sinong Wang},\nTitle = {LM-Infinite: Simple On-the-Fly Length Generalization for Large Language Models},\nYear = {2023},\nEprint = {arXiv:2308.16137},\n}\n```',
    'author': 'Kye Gomez',
    'author_email': 'kye@apac.ai',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/kyegomez/LM-Infinite',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
