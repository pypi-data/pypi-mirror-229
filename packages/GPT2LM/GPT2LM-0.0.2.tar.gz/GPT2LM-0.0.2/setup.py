from setuptools import setup, find_packages
import setuptools

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='GPT2LM',
    version='0.0.2',
    description='Implementation of GPT-2 language model for text generation, training custom models and fine-tuning.',
    long_description=long_description,
    author='Yashraj Baila',
    url="https://github.com/YashrajBaila7/GPT2LM",
    author_email='yashrajbailapython@gmail.com',
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages('src'),
    keywords=['gpt2lm', 'GPT2LM', 'gpt', 'GPT', 'Language model', 'Yashraj Baila',
              'AI', 'Artificial Intelligence', 'ML', 'Meachine Learning', 'Deep Learning', 'GPT2', 'gpt2'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    python_requires='>=3.9',
    package_dir={'': 'src'},
    install_requires=[
        'yashpyproject',
        'torch',
        'tqdm'
    ],
)
