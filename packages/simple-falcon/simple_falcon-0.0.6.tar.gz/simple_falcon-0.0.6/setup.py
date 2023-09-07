# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['falcon']

package_data = \
{'': ['*']}

install_requires = \
['accelerate', 'bitsandbytes', 'torch', 'transformers']

setup_kwargs = {
    'name': 'simple-falcon',
    'version': '0.0.6',
    'description': 'Falcon - Pytorch',
    'long_description': '[![Multi-Modality](agorabanner.png)](https://discord.gg/qUtxnK2NMf)\n\n# Simple Falcon\nA simple package for leveraging Falcon 180B and the HF ecosystem\'s tools, including training/inference scripts, safetensors, integrations with bitsandbytes, PEFT, GPTQ, assisted generation, RoPE scaling support, and rich generation parameters.\n\n\n## Installation\n\nYou can install the package using pip\n\n```bash\npip3 install simple-falcon\n```\n---\n\n# Usage\n\n```python\nfrom falcon.main import Falcon\n\n\nfalcon = Falcon(\n    temperature=0.5, \n    top_p=0.9, \n    max_new_tokens=500,\n    quantized=True,\n    system_prompt=""\n)\n\nprompt = "What is the meaning of the collapse of the wave function?"\n\nresult = falcon.run(prompt=prompt)\nprint(result)\n```\n\n# Documentation\n\nThe Falcon class provides a convenient interface for conversational agents based on the transformers architecture. It facilitates both single-turn and multi-turn conversations with pre-trained models and allows users to customize certain inference settings such as `temperature`, `top_p`, and token generation limits. Furthermore, it can leverage quantized models for faster performance.\n\n### Purpose\n\nThe main purpose of the Falcon class is to:\n- Make it easy to initiate and run generative language models.\n- Provide efficient conversation interfaces with customization.\n- Support both regular and quantized models for better performance.\n- Manage conversational history in multi-turn scenarios.\n\n### Class Definition:\n\n```python\nclass Falcon:\n    def __init__(\n        self,\n        *,\n        model_id: str = "tiiuae/falcon-180B",\n        temperature: float = None,\n        top_p: float = None,\n        max_new_tokens: int = None,\n        quantized: bool = False,\n        system_prompt: str = None\n    ):\n```\n\n#### Parameters:\n\n- **model_id (str)**: Model identifier from the HuggingFace Model Hub. Default is "tiiuae/falcon-180B".\n  \n- **temperature (float, optional)**: Controls randomness in the Boltzmann distribution of model predictions. Higher values result in more randomness.\n  \n- **top_p (float, optional)**: Nucleus sampling: Restricts sampling to the top tokens summing up to this cumulative probability.\n  \n- **max_new_tokens (int, optional)**: Maximum number of tokens that can be generated in a single inference call.\n  \n- **quantized (bool)**: If set to `True`, the model loads in 8-bit quantized mode. Default is `False`.\n  \n- **system_prompt (str, optional)**: Initial system prompt to set the context for the conversation.\n\n### Method Descriptions:\n\n#### 1. run:\n\n```python\ndef run(self, prompt: str) -> None:\n```\n\nGenerates a response based on the provided prompt.\n\n**Parameters**:\n- **prompt (str)**: Input string to which the model responds.\n\n**Returns**: None. The response is printed to the console.\n\n#### 2. chat:\n\n```python\ndef chat(self, message: str, history: list[tuple[str, str]], system_prompt: str = None) -> None:\n```\n\nGenerates a response considering the conversation history.\n\n**Parameters**:\n- **message (str)**: User\'s current message to which the model will respond.\n  \n- **history (list[tuple[str, str]])**: Conversation history as a list of tuples. Each tuple consists of the user\'s prompt and the Falcon\'s response.\n  \n- **system_prompt (str, optional)**: Initial system prompt to set the context for the conversation.\n\n**Returns**: None. The response is printed to the console.\n\n### Usage Examples:\n\n#### 1. Single-turn conversation:\n\n```python\nfrom simple_falcon import Falcon\nimport torch\n\nmodel = Falcon(temperature=0.8)\nmodel.run("What is the capital of France?")\n```\n\n#### 2. Multi-turn conversation with history:\n\n```python\nfrom simple_falcon import Falcon\nimport torch\n\nmodel = Falcon(system_prompt="Conversational Assistant")\nhistory = [\n    ("Hi there!", "Hello! How can I assist you?"),\n    ("What\'s the weather like?", "Sorry, I can\'t fetch real-time data, but I can provide general info.")\n]\nmodel.chat("Tell me a joke.", history)\n```\n\n#### 3. Using quantized models:\n\n```python\nfrom simple_falcon import Falcon\nimport torch\n\nmodel = Falcon(quantized=True)\nmodel.run("Tell me about quantum computing.")\n```\n\n### Mathematical Representation:\n\nThe Falcon class essentially leverages the transformer-based generative language model for text generation. The mathematical process can be generalized as:\n\nGiven an input sequence \\( x = [x_1, x_2, ... , x_n] \\), the model predicts the next token \\( x_{n+1} \\) by:\n\n\\[ x_{n+1} = \\arg \\max P(x_i | x_1, x_2, ... , x_n) \\]\n\nWhere:\n- \\( P \\) is the probability distribution over the vocabulary generated by the model.\n- The argmax operation selects the token with the highest probability.\n\n### Additional Information:\n\n- For best performance, it\'s recommended to use the Falcon class with CUDA-enabled devices. Ensure that your PyTorch setup supports CUDA.\n  \n- The Falcon class uses models from the HuggingFace model hub. Ensure you have an active internet connection during the first run as models will be downloaded.\n  \n- If memory issues arise, consider reducing the `max_new_tokens` parameter or using quantized models.\n\n---\n\n# License\nMIT\n\n\n\n',
    'author': 'Kye Gomez',
    'author_email': 'kye@apac.ai',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/kyegomez/Falcon',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
