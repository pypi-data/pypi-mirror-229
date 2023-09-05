# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['profit']

package_data = \
{'': ['*']}

install_requires = \
['beautifulsoup4',
 'clarifai',
 'faiss-gpu==1.7.2',
 'google-api-python-client',
 'google-auth-httplib2',
 'google-auth-oauthlib',
 'langchain',
 'langchain-experimental',
 'openai',
 'pandas',
 'pydantic',
 'torch',
 'transformers']

setup_kwargs = {
    'name': 'profit-pilot',
    'version': '0.1.7',
    'description': 'ProfitPilot - AI Agents',
    'long_description': '# ProfitPilot\nIntroducing ProfitPilot, your ultimate autonomous AI sales professional agent. With our cutting-edge technology, we revolutionize the way businesses drive profits and skyrocket their sales.\n\nImagine having a highly skilled sales professional who works tirelessly for you, always ready to engage clients, close deals, and generate revenue. \n\nThat\'s exactly what ProfitPilot offers – a seductive value proposition that guarantees increased profitability and accelerated growth for your business.\n\nProfitPilot combines powerful artificial intelligence with deep learning algorithms, enabling it to understand customer behaviors, preferences, and purchase patterns better than any human salesperson. \n\nIt captivates potential clients with its persuasive communication skills, building lasting relationships and creating repeat customers.\n\nSay goodbye to wasted resources on hiring and training sales staff, as ProfitPilot works 24/7, tirelessly prospecting, qualifying leads, and delivering personalized pitches. \n\nIts effortless adaptability allows it to navigate through different industries, ensuring your value proposition resonates flawlessly with every client.\n\nBut that\'s not all. \n\nProfitPilot\'s unparalleled ability to analyze big data means it can identify market trends, predict customer demands, and provide you with valuable insights to stay ahead of the competition. \n\nIt becomes your reliable co-pilot, guiding your business towards profitable decisions and unlocking hidden revenue streams.\n\nWith ProfitPilot, you\'ll experience unrivaled efficiency, precision, and revenue generation in your sales process. \n\nBy leveraging the power of autonomous AI, you unlock endless possibilities for sustainable growth, increased ROI, and a competitive edge in any market.\n\nDon\'t settle for outdated sales strategies. Embrace the future of selling with ProfitPilot – your ultimate seductive value proposition that guarantees an unstoppable surge in profits and takes your business to soaring heights.\n\n---\n\n# Installation\n```pip install profit-pilot```\n\n# Usage\n```python\nfrom profit.main import ProfitPilot\n\n\n\n# Create an instance of the ProfitPilot class\npilot = ProfitPilot(\n    openai_api_key="YOUR_OPENAI_API_KEY",\n    ai_name="Athena",\n    ai_role="Sales Representative",\n    external_tools=None,\n    company_name="ABC Company",\n    company_values="Quality, Innovation, Customer Satisfaction",\n    conversation_type="Cold Call",\n    conversation_purpose="discuss our new product",\n    company_business="Software Development",\n    salesperson_name="John Doe",\n    human_in_the_loop=False\n)\n\n# Define the task you want the agent to perform\ntask = "Hello, I\'m calling to discuss our new product. Can I speak with the decision-maker?"\n\n# Run the task using the ProfitPilot instance\npilot.run(task)\n\n```\n# Todo\n- Worker\n- Prompt,\n- Tools, Zapier tool, email answering, summarizng, email understanding, email response\n- Lead scraping, create tool that scrapes that scrapes on a website domain\n\n\n## Requirements\n- Email function tools\n- Zapier tools\n- Prompts\n- pdf tool\n\n\n# TO win Hackathon\n- Focus on the story, why we\'re building this\n- Build a seamless user experience\n\n\n-----\n\n![Clarifai logo](https://www.clarifai.com/hs-fs/hubfs/logo/Clarifai/clarifai-740x150.png?width=240)\n\n# Clarifai App Module Template\n\nThis is a template repository to make it easy to get started creating a UI module with Clarifai.\n\n\n## To use this repo\n\n1. Click the "Use this template" green button on github to make a repo from this repo template and give it a name of the format module-{XYZ} filling in the XYZ portion. \n2. Clone the new repo as normal to your development environment.\n3. `pip install -r requirements.txt` to make sure you have all the Python packages installed. Add any new packages to this requirements.txt file that you add during development.\n4. Update the README.md to capture what your new module will do.\n5. Rename the pages/*.py files as you desire and start filling them in to implement your module.\n6. After you\'re tried things out locally, push your changes to github and get the git commit URL from there in order to create a module in Clarifai. \n7. Go to any app you can create in within Clarifai, select Modules on the left and "Create Module" button, then follow the steps.\n\n',
    'author': 'Kye Gomez',
    'author_email': 'kye@apac.ai',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/kyegomez/ProfitPilot',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
