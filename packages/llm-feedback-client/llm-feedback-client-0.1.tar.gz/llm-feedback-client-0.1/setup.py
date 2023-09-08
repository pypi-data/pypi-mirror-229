from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='llm-feedback-client',
    version='0.1', 
    packages=find_packages(),
    author='Chunyang Shen',
    author_email='scy0208@gmail.com',
    description='A Python client for the LLM Feedback API.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/scy0208/llm-feedback-client-py',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires=[
        'requests',
    ],
    python_requires='>=3.6',
)
