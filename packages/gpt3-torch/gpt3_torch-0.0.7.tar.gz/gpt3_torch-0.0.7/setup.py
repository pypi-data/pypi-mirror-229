# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gpt3', 'gpt3.utils']

package_data = \
{'': ['*']}

install_requires = \
['SentencePiece',
 'accelerate',
 'datasets',
 'deepspeed',
 'einops',
 'lion-pytorch',
 'matplotlib',
 'numpy',
 'torch',
 'transformers',
 'zetascale']

setup_kwargs = {
    'name': 'gpt3-torch',
    'version': '0.0.7',
    'description': 'GPT3 - Pytorch',
    'long_description': '[![Multi-Modality](agorabanner.png)](https://discord.gg/qUtxnK2NMf)\n\n\n# GPT-3: Few-Shot Learning for Language Models\n\n\n\n\n## 💻 Installation\n\n`pip install gpt3-torch`\n\n---\n\n\n## Code Example\n\nHere\'s an illustrative code snippet that showcases GPT-3 in action:\n\n\n```python\nimport torch\nfrom gpt3.gp3 import GPT3\n\n# Generate a random input sequence\nx = torch.randint(0, 256, (1, 1024)).cuda()\n\n# Initialize GPT-3 model\nmodel = GPT3()\n\n# Pass the input sequence through the model\noutput = model(x)\n```\n\n\n### 📚 Training\n\n```python\nfrom gpt3 import train\n\ntrain()\n\n```\n\nFor further instructions, refer to the [Training SOP](DOCs/TRAINING.md).\n\n\n1. Set the environment variables:\n   - `ENTITY_NAME`: Your wandb project name\n   - `OUTPUT_DIR`: Directory to save the weights (e.g., `./weights`)\n   - `MASTER_ADDR`: For distributed training\n   - `MASTER_PORT` For master port distributed training\n   - `RANK`- Number of nodes services\n   - `WORLD_SIZE` Number of gpus\n\n2. Configure the training:\n   - Accelerate Config\n   - Enable Deepspeed 3\n   - Accelerate launch train_distributed_accelerate.py\n\nFor more information, refer to the [Training SOP](DOCs/TRAINING.md).\n\n\n\n\n---\n\nWelcome to the repository for GPT-3: Few-Shot Learning for Language Models! This repository provides code examples and insights related to the groundbreaking paper "Language Models are Few-Shot Learners" by Tom B. Brown et al. Explore the potential of GPT-3, a language model with 175 billion parameters, and its remarkable few-shot learning capabilities. Below, we provide an overview of key concepts, practical code snippets, and the paper\'s findings.\n\n## Introduction\n\nIn recent years, Natural Language Processing (NLP) has witnessed remarkable progress through pre-training language models on vast text corpora and fine-tuning them for specific tasks. However, these models still demand substantial task-specific data to excel. This paper introduces a paradigm shift by unveiling the concept of few-shot learning for language models. Discover how the scale of the model impacts its performance, akin to humans learning from just a few examples or simple instructions.\n\n## Methodology\n\nThis paper introduces GPT-3, an autoregressive language model with a groundbreaking scale of 175 billion parameters. The authors assess GPT-3\'s few-shot learning capabilities by subjecting it to various tasks without any gradient updates or fine-tuning. The model\'s understanding of tasks and demonstrations is achieved solely through text interactions.\n\n## Results\n\nThe paper presents compelling results highlighting GPT-3\'s prowess in few-shot learning:\n\n- **Translation**\n- **Question-answering**\n- **Cloze tasks**\n- **On-the-fly reasoning**\n- **Domain adaptation tasks**\n\nFurthermore, GPT-3 excels in tasks that involve unscrambling words, incorporating novel words into sentences, and performing 3-digit arithmetic. While demonstrating its potential, the paper acknowledges areas where GPT-3\'s few-shot learning encounters challenges, opening avenues for future enhancement. Additionally, methodological concerns related to training language models on extensive web corpora are discussed.\n\n## Conclusion\n\nThe study concludes that scaling up model size, as exemplified by GPT-3, substantially elevates few-shot learning capabilities. GPT-3 achieves competitive results compared to state-of-the-art fine-tuning approaches. The authors delve into the broader implications of GPT-3\'s capabilities, including its potential to generate human-like text. The paper emphasizes the need for ongoing research to address challenges in challenging few-shot learning tasks and to address methodological concerns associated with large web corpora training.\n\nFor a comprehensive understanding of the paper\'s methodologies, insights, and findings, refer to the original publication: [Language Models are Few-Shot Learners](https://doi.org/arXiv.2005.14165).\n\nIf you find this repository valuable, consider starring it or contributing to foster continual exploration and discourse in the field of NLP and few-shot learning.',
    'author': 'Kye Gomez',
    'author_email': 'kye@apac.ai',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/kyegomez/gpt3',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
