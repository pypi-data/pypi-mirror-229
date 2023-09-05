# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['chainfury',
 'chainfury.components',
 'chainfury.components.ai_actions',
 'chainfury.components.chroma',
 'chainfury.components.functional',
 'chainfury.components.milvus',
 'chainfury.components.nbx',
 'chainfury.components.openai',
 'chainfury.components.pinecone_db',
 'chainfury.components.qdrant',
 'chainfury.components.redis',
 'chainfury.components.serper',
 'chainfury.components.stability',
 'chainfury.components.tune']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2==3.1.2',
 'fire==0.5.0',
 'jinja2schema==0.1.4',
 'pydantic>=1.10.7,<2.0.0',
 'requests>=2.28.2,<3.0.0']

extras_require = \
{'all': ['stability-sdk==0.8.3', 'qdrant-client==1.3.1', 'boto3==1.28.15'],
 'qdrant': ['qdrant-client==1.3.1'],
 'stability': ['stability-sdk==0.8.3']}

entry_points = \
{'console_scripts': ['cf = chainfury.cli:main',
                     'chainfury = chainfury.cli:main']}

setup_kwargs = {
    'name': 'chainfury',
    'version': '1.4.3',
    'description': 'ChainFury is a powerful tool that simplifies the creation and management of chains of prompts, making it easier to build complex chat applications using LLMs.',
    'long_description': '# 🦋 NimbleBox ChainFury\n\n[![linkcheck](https://img.shields.io/badge/Workflow-Passing-darkgreen)](https://github.com/NimbleBoxAI/ChainFury/actions)\n[![Downloads](https://static.pepy.tech/badge/chainfury)](https://pepy.tech/project/chainfury)\n[![linkcheck](https://img.shields.io/badge/Site-🦋ChainFury-lightblue)](https://chainfury.nbox.ai)\n[![License: Apache](https://img.shields.io/badge/License-Apache%20v2.0-red)](https://github.com/NimbleBoxAI/ChainFury/blob/main/LICENSE) \n[![Twitter](https://img.shields.io/twitter/url/https/twitter.com/NimbleBoxAI.svg?style=social&label=Follow%20%40NimbleBoxAI)](https://twitter.com/NimbleBoxAI)\n[![](https://dcbadge.vercel.app/api/server/KhF38hrAJ2?compact=true&style=flat)](https://discord.com/invite/KhF38hrAJ2)\n\n🦋 Build complex chat apps using LLMs in 4 clicks ⚡️ [Try it out here](https://chainfury.nbox.ai/). Used in production by [chat.nbox.ai](https://chat.nbox.ai).\n\n# Read the [Docs](https://nimbleboxai.github.io/ChainFury/index.html)\n\nThe documentation page contains all the information on using `chainfury` and `chainfury_server`.\n\n# Installation\n\nThere are two separate packages built into this repository, first is `chainfury` which contains the fury-engine for running\nthe DAGs and `chainfury_server` which contains the self hosted server for the GUI.\n\n``` bash\npip install chainfury\npip install chainfury_server\n\n# to launch the server\npython3 -m chainfury_server\n```\n\n### Run Docker\n\nEasiest way to run the server is to use docker. You can use the following command to run ChainFury:\n\n```bash\ndocker build . -f Dockerfile -t chainfury:latest\ndocker run -p 8000:8000 chainfury:latest\n```\n\nTo pass any env variables you can use the command:\n\n```bash\ndocker run --env ENV_KEY=ENV_VALUE -p 8000:8000 chainfury:latest\n```\n\nCheckout all the:\n- `component` environment variables [here](https://nimbleboxai.github.io/ChainFury/source/chainfury.components.const.html#chainfury.components.const.Env)\n- `chainfury` specific variables [here](https://nimbleboxai.github.io/ChainFury/source/chainfury.utils.html#chainfury.utils.CFEnv)\n- `chainfury_server` specific variables [here](https://nimbleboxai.github.io/ChainFury/cf_server/chainfury_server.commons.config.html#chainfury_server.commons.config.Env)\n\n### From Source\n\nHere\'s a breakdown of folder:\n\n- `chainfury/` contains the chainfury engine\n- `server/` contains the chainfury server\n- `client/` contains the frontend code for the GUI\n- `api_docs/` contains the documentation\n\nTo build the entire system from scratch follow these steps:\n\n```bash\ngit clone https://github.com/NimbleBoxAI/ChainFury\ncd ChainFury\npython3 -m venv venv\nsource venv/bin/activate\n```\n\nYou will need to have `yarn` installed to build the frontend and move it to the correct location on the server\n\n```bash\nsh stories/build_and_copy.sh\n```\n\nOnce the static files are copied we can now proceed to install dependecies:\n\n```bash\npip install setuptools\npip install -e .          # editable install the chainfury\ncd server\npip install -e .          # editable install the chainfury_server\n```\n\nTo start you can now do:\n\n```bash\ncd chainfury_server\npython3 server.py\n```\n\nYou can now visit [localhost:8000](http://localhost:8000/ui/) to see the GUI.\n\n# Contibutions\n\nChainFury is an open-source project used in production. We are open to contributions to the project in the form of features,\ninfrastructure or documentation.\n\n- Our [issues](https://github.com/NimbleBoxAI/ChainFury/issues) page is kept up to date with bugs, improvements, and feature requests.\n\n- If you\'re looking for help with your code, hop onto [GitHub Discussions board](https://github.com/NimbleBoxAI/ChainFury/discussions) or\n[Discord](https://discord.com/invite/KhF38hrAJ2), so that more people can benefit from it.\n\n- **Describing your issue:** Try to provide as many details as possible. What exactly goes wrong? How is it failing?\nIs there an error? "XY doesn\'t work" usually isn\'t that helpful for tracking down problems. Always remember to include\nthe code you ran and if possible, extract only the relevant parts and don\'t just dump your entire script. This will make\nit easier for us to reproduce the error.\n\n- **Sharing long blocks of code or logs:** If you need to include long code, logs or tracebacks, you can wrap them in\n`<details>` and `</details>`. This [collapses the content](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/details)\nso it only becomes visible on click, making the issue easier to read and follow.\n\n',
    'author': 'NimbleBox Engineering',
    'author_email': 'engineering@nimblebox.ai',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/NimbleBoxAI/ChainFury',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<3.12',
}


setup(**setup_kwargs)
