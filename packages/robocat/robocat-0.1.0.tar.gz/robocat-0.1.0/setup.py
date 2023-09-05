# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['robocat', 'robocat.utils']

package_data = \
{'': ['*']}

install_requires = \
['beartype',
 'classifier-free-guidance-pytorch',
 'dalle-pytorch',
 'diffusers',
 'einops',
 'palm-rlhf-pytorch',
 'palme',
 'tokenizers',
 'torch',
 'transformers',
 'wandb']

setup_kwargs = {
    'name': 'robocat',
    'version': '0.1.0',
    'description': 'Robo CAT- Pytorch',
    'long_description': '[![Multi-Modality](agorabanner.png)](https://discord.gg/qUtxnK2NMf)\n\n\n# ROBOTCAT\n![ROBOCAT MODELS](robocat.png)\n\nRoboCAT is a self-improving foundation agent for robotic manipulation developed by DeepMind Robotics. The model architecture of RoboCAT is similar to the RT-1 model. It follows a tokenization approach where robotics images, proprioception, and future actions are tokenized. \n\n* Help with the implementation in the Agora discord, ![Discord](https://img.shields.io/discord/999382051935506503)\n\n----\n\n# Install\n`pip install robotcat`\xa0\n\n---\n\n## Basic Usage\n\n```python\nimport torch \nfrom robocat.model import RoboCat\n\nmodel = RoboCat()\n\nvideo = torch.randn(2, 3, 6, 224, 224)\ninstructions = [\n    "bring me that apple"\n]\n\nresult = model.forward(video, instructions)\nprint(result)\n\n```\n\n\n## Generate Data\n* RoboCat can self generate data with images and or video, to use simply use the generator classes -> then tokenize and or tensorize using your custom strategy\n\n```python\n#for images\nfrom robotcat import ImageDataGenerator\n\ngenerator = ImageDataGenerator()\n\nprompt = "Robot picking up cup in kitchen"\ngenerator.generate(prompt)\n```\n\nand or for videos\n\n```python\nfrom robocat import VideoDataGenerator, RoboCat\n\ngenerator = VideoDataGenerator()\nmodel = RoboCat()\n\nprompt = "Robot picking up cup in kitchen in first person"\nvideo = generator.generate(prompt)\nvideo = transform_to_tensors(video) #(batch, frames, actions, bins)\n\nmodel(video, prompt)\n\n```\n----\n\n\n## Architecture\nThe architecture consists of the following key components:\n\n1. Tokenizer: RoboCAT learns a tokenizer for robotics images. It tokenizes proprioception and future actions in a straightforward manner, enabling the prediction of future action tokens.\n\n2. Transformer Model: The tokenized inputs are fed into a Transformer model. The Transformer model predicts future action sequences based on the input tokens. This allows the model to perform a wide range of robotic tasks using a unified interface.\n\n3. Action Spaces: RoboCAT predicts Cartesian 4 or 6 degrees of freedom (DoF) cartesian velocities for the arm and 1 DoF (parallel jaw gripper) or 8 DoF (3-finger) for the hand. This flexible approach enables the model to handle action spaces of different sizes and variable proprioception sizes.\n\nThe architecture of RoboCAT allows for the integration of multiple robot embodiments with a unified interface. By predicting the appropriate number of tokens based on the robot\'s morphology, the model can effectively scale without the need for separate prediction heads for each embodiment.\n\n\n## Misc Components\n\n### Generalization and Transfer Learning\nThe RoboCAT paper focuses on studying generalization and transfer learning. It explores how training on one domain benefits testing on another and investigates the effectiveness of transfer learning from simulation to the real world. The authors provide empirical data on cross-task transfer, architecture scaling, and tokenization strategies for perception.\n\n### Evaluation and Automated Testing\nRoboCAT emphasizes the importance of rigorous evaluation and presents methodologies for automated evaluation of multi-task policies in real-world settings. The paper provides details on evaluation protocols, data collection, and comparative analysis of different models and approaches.\n\n### Real-World Robotic Tasks\nThe paper highlights the challenges of real-world robotics tasks and the significance of cross-robot transfer. The authors showcase consistent results across multiple robots and action spaces, demonstrating the value of collecting real-world data for training and evaluation. The effort put into data set detailing and evaluation protocols is commendable.\n\n### Future Directions and Reproducibility\nThe authors acknowledge the ongoing challenge of reproducibility in robotics research. They emphasize the need for independent replication in different labs and variations in manipulation tasks and hardware. The paper raises questions about the impact of experimental choices and engineering decisions on research outcomes and\n\n calls for advancements in evaluation methodologies.\n\n## Conclusion\n\nThe RoboCAT paper presents a self-improving foundation agent for robotic manipulation that addresses the challenges of generalization and transfer learning in the field of robotics. It offers insights into the model architecture, requirements, and experimental findings. The extensive empirical data, evaluation protocols, and comparisons provide valuable contributions to the research community.\n\n# Roadmap\n\n* Functional prototype\n\n* Integrate VQGAN to generate an image when it has not encountered an known environment\n\n` environment observation -> environment familarity rating [0.0-1.0] -> generate data if lower then [0.5] -> finetune -> action`\n\n* Train on massive datasets\n\n* Finetune as specified on paper\n\n* Release as paid API\n\n* Integrate more modalities like hearing, 3d mapping, nerfs, videos, lidar, locomotion, and the whole lot!\n\n\n## Citations\n\n```bibtex\n@article{Bousmalis2023RoboCat,\n    title   = {RoboCat: A Self-Improving Foundation Agent for Robotic Manipulation},\n    author  = {Konstantinos Bousmalis*, Giulia Vezzani*, Dushyant Rao*, Coline Devin*, Alex X. Lee*, Maria Bauza*, Todor Davchev*, Yuxiang Zhou*, Agrim Gupta*,1, Akhil Raju, Antoine Laurens, Claudio Fantacci, Valentin Dalibard, Martina Zambelli, Murilo Martins, Rugile Pevceviciute, Michiel Blokzijl, Misha Denil, Nathan Batchelor, Thomas Lampe, Emilio Parisotto, Konrad Żołna, Scott Reed, Sergio Gómez Colmenarejo, Jon Scholz, Abbas Abdolmaleki, Oliver Groth, Jean-Baptiste Regli, Oleg Sushkov, Tom Rothörl, José Enrique Chen, Yusuf Aytar, Dave Barker, Joy Ortiz, Martin Riedmiller, Jost Tobias Springenberg, Raia Hadsell†, Francesco Nori† and Nicolas Heess},\n    journal = {ArXiv},\n    year    = {2023}\n}\n```\n\n\n\n',
    'author': 'Kye Gomez',
    'author_email': 'kye@apac.ai',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/kyegomez/RoboCAT',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
