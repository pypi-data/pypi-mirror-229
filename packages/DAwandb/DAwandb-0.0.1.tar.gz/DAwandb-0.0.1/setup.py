from setuptools import setup

setup(
    name='DAwandb',
    version='0.0.1',
    author='KKR',
    author_email='alfmalfm11@yonsei.ac.kr',
    description='this package basic wandb',
    packages=['DAwandb'],
    install_requires=['tqdm','numpy', 'wandb', 'torch','torchvision'],
)