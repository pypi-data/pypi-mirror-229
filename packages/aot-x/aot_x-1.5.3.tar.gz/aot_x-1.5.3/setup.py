# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aot']

package_data = \
{'': ['*']}

install_requires = \
['swarms']

setup_kwargs = {
    'name': 'aot-x',
    'version': '1.5.3',
    'description': 'Algorithm of thoughts - Pytorch',
    'long_description': '[![Multi-Modality](agorabanner.png)](https://discord.gg/qUtxnK2NMf)\n\n# Algorithm-Of-Thoughts\n![AOT BANNER](aot.png)\nThe open source implementation of "Algorithm of Thoughts: Enhancing Exploration of Ideas in Large Language Models"\n\n[Algorithm of Thoughts: Enhancing Exploration of Ideas in Large Language Models](https://arxiv.org/abs/2308.10379)\n\n# Installation\n`pip install aot-x`\n\n\n# Usage\n```python\nfrom aot import AoT\n\nsystem_prompt = """\n\nUse numbers and basic arithmetic operations (+ - * /) to obtain 24. When\nconsidering the next steps, do not choose operations that will result in a\nnegative or fractional number. In order to help with the calculations, the\nnumbers in the parenthesis represent the numbers that are left after the\noperations and they are in descending order.\nAnother thing we do is when there are only two numbers left in the parenthesis, we\ncheck whether we can arrive at 24 only by using basic arithmetic operations\n(+ - * /). Some examples regarding this idea:\n(21 2) no\nsince 21 + 2 = 23, 21 - 2 = 19, 21 * 2 = 42, 21 / 2 = 10.5, none of which is equal\nto 24.\n(30 6) 30 - 6 = 24 yes\n(8 3) 8 * 3 = 24 yes\n(12 8) no\n(48 2) 48 / 2 = 24 yes\nMost importantly, do not give up, all the numbers that will be given has indeed a\nsolution.\n\n14 8 8 2\n"""\n\n\ntask = "5 10 5 2 "\n\n\naot = AoT(task=task, system_prompt=system_prompt)\naot.run()\n```\n\n# Todo\n- [ ] All thoughts over 0.5 are added to cache or longterm vectorstore \n- [ ] DFS search similiar to tree of thoughts\n- [ ] Propose solutions function\n- [ ] Backtrack to nearest successful states\n- [ ] Implement evaluation strategy similiar to tot with [0.0, 1.0]\n- [ ] Working demo: Conducts search then backtracks through states, provide visuals green text\n- [ ] Streamlit demo\n\n\n## Citation\n```\n@misc{2308.10379,\nAuthor = {Bilgehan Sel and Ahmad Al-Tawaha and Vanshaj Khattar and Lu Wang and Ruoxi Jia and Ming Jin},\nTitle = {Algorithm of Thoughts: Enhancing Exploration of Ideas in Large Language Models},\nYear = {2023},\n```',
    'author': 'Kye Gomez',
    'author_email': 'kye@apac.ai',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/kyegomez/Algorithm-Of-Thoughts',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
